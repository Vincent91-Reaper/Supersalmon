import os
import re
import shutil
from collections import namedtuple
from itertools import chain
from string import Formatter

import click

from brucelee94 import cfg
from brucelee94.constants import (
    ARROWS,
    BLACKLISTED_CHARS,
    BLACKLISTED_FULLWIDTH_REPLACEMENTS,
)
from brucelee94.tagger.tagfile import TagFile

Change = namedtuple("Change", ["tag", "old", "new"])


def tag_files(path, tags, metadata, auto_rename, source_url=None):
    """
    Wrapper function that calls the functions that create and print the
    proposed changes, and automatically applies tags without prompting.
    """
    if not check_whether_to_tag(tags, metadata, source_url):
        return
    
    # Check if source is Apple Music / iTunes
    is_apple_music = source_url and ("music.apple.com" in source_url or "itunes.apple.com" in source_url)
    
    album_changes = collect_album_data(metadata)
    track_changes = create_track_changes(tags, metadata, preserve_artists=is_apple_music)
    
    # Only print "Retagging files..." if there are actual changes to make
    if any(t for t in track_changes.values()):
        click.secho("\nRetagging files...", fg="cyan", bold=True)
        print_changes(album_changes, track_changes, next(iter(tags.values())))
        # Auto-tag files without confirmation prompt
        retag_files(path, album_changes, track_changes, preserve_artists=is_apple_music)


def check_whether_to_tag(tags, metadata, source_url=None):
    """
    Make sure the number of tracks in the metadata equals the number of tracks
    in the folder. For Tidal, skip this check as track structure may differ.
    """
    # Skip track count check for Tidal sources
    is_tidal = source_url and ("tidal.com" in source_url or "wimpmusic.com" in source_url)
    if is_tidal:
        return True
        
    if len(tags) != sum([len(disc) for disc in metadata["tracks"].values()]):
        click.secho(
            "Number of tracks differed from number of tracks in metadata, skipping retagging procedure...",
            fg="red",
        )
        return False
    return True


def collect_album_data(metadata):
    """Create a dictionary of the proposed album tags (consistent across every track).
    Changed: No longer tags files with label, catno, or albumartist.
    Artist tags are validated and updated to match scraped metadata."""
    # Return empty dict - we don't apply album-level tags to files anymore
    return {}


def _generate_album_artist(artists):
    main_artists = [a for a, i in artists if i == "main"]
    if len(main_artists) >= cfg.upload.formatting.various_artist_threshold:
        return cfg.upload.formatting.various_artist_word
    c = ", " if len(main_artists) > 2 or "&" in "".join(main_artists) else " & "
    return c.join(sorted(main_artists))


def create_track_changes(tags, metadata, preserve_artists=False):
    """
    Compare the track data in the metadata to the track data in the tags
    and auto-tag with correct artists from scraped metadata.
    Only retags main artists (and composers for classical albums).
    
    Args:
        preserve_artists: If True (for Apple Music), don't modify artist tags
    """
    changes = {}
    tracks = metadata_to_track_list(metadata["tracks"])
    
    # Check if this is a classical album
    is_classical = "Classical" in metadata.get("genres", [])
    
    for (filename, tagset), trackmeta in zip(tags.items(), tracks, strict=False):
        changes[filename] = []
        
        # Auto-tag artists from scraped metadata (unless preserve_artists is True for Apple Music)
        if not preserve_artists:
            try:
                old_artist_str = ", ".join(tagset.artist) if tagset.artist else "None"
            except (TypeError, AttributeError):
                old_artist_str = "None"

            # Get the correct artist string from scraped metadata (main artists only)
            new_artist_str = create_main_artist_str(trackmeta["artists"], is_classical)
            
            # Update artist tag if it's missing OR the actual artist names are different
            # Normalize comparison to ignore order and separator differences
            if old_artist_str == "None" or not old_artist_str:
                changes[filename].append(Change("artist", old_artist_str, new_artist_str))
            elif not _artists_match(old_artist_str, new_artist_str):
                changes[filename].append(Change("artist", old_artist_str, new_artist_str))

    return changes


def append_guests_to_track_titles(track):
    guest_artists = [a for a, i in track["artists"] if i == "guest"]
    if (
        "feat" not in track["title"]
        and guest_artists
        and len(guest_artists) <= cfg.upload.formatting.various_artist_threshold
    ):
        c = ", " if len(guest_artists) > 2 or "&" in "".join(guest_artists) else " & "
        # If we find a remix parenthetical, remove it and re-add it after the guest artists.
        remix = re.search(r"( \([^\)]+Remix(?:er)?\))", track["title"], flags=re.IGNORECASE)
        if remix:
            track["title"] = track["title"].replace(remix[1], "")
        track["title"] += f" (feat. {c.join(sorted(guest_artists))})"
        if remix:
            track["title"] += remix[1]
    return track["title"]


def metadata_to_track_list(metadata):
    """Turn the double nested dictionary of tracks into a flat list of tracks."""
    return list(chain.from_iterable([d.values() for d in metadata.values()]))


def _compare_tag(tagfield, metafield, tagset, trackmeta):
    """
    Compare a tag to the equivalent metadata field. If the metadata field
    does not equal the existing tag, return a ``Change``.
    """
    if trackmeta[metafield]:
        if not getattr(tagset, tagfield, False):
            return Change(tagfield, None, trackmeta[metafield])
        if str(getattr(tagset, tagfield, "")) != str(trackmeta[metafield]):
            return Change(tagfield, getattr(tagset, tagfield, "None"), trackmeta[metafield])
    return None


def create_artist_str(artists):
    """Create the artist string from the metadata. It can contain main and guests."""
    main_artists = [a for a, i in artists if i == "main"]
    c = ", " if len(main_artists) > 2 and "&" not in "".join(main_artists) else " & "
    artist_str = c.join(sorted(main_artists))

    if not cfg.upload.formatting.guests_in_track_title:
        guest_artists = [a for a, i in artists if i == "guest"]
        if len(guest_artists) >= cfg.upload.formatting.various_artist_threshold:
            artist_str += f" (feat. {cfg.upload.formatting.various_artist_word})"
        elif guest_artists:
            c = ", " if len(guest_artists) > 2 and "&" not in "".join(guest_artists) else " & "
            artist_str += f" (feat. {c.join(sorted(guest_artists))})"

    return artist_str


def create_main_artist_str(artists, is_classical=False):
    """
    Create the artist string with ONLY main artists (and composers for classical).
    No guest/featured artists, remixers, compilers, DJs, etc.
    """
    main_artists = [a for a, i in artists if i == "main"]
    c = ", " if len(main_artists) > 2 and "&" not in "".join(main_artists) else " & "
    artist_str = c.join(sorted(main_artists))
    
    # For classical albums, also include composers
    if is_classical:
        composers = [a for a, i in artists if i == "composer"]
        if composers:
            c_comp = ", " if len(composers) > 2 and "&" not in "".join(composers) else " & "
            composer_str = c_comp.join(sorted(composers))
            if artist_str and composer_str:
                artist_str = f"{composer_str}; {artist_str}"
            elif composer_str:
                artist_str = composer_str
    
    return artist_str


def _artists_match(old_artist_str, new_artist_str):
    """
    Check if two artist strings contain the same artists, regardless of order or separator.
    This prevents unnecessary retagging when artists are the same but formatted differently.
    
    Example: "Hannah Boleyn & Punctual" matches "Punctual, Hannah Boleyn"
    """
    # Normalize both strings: split by common separators and create sets of artist names
    def normalize_artists(artist_str):
        # Replace common separators with a single delimiter
        normalized = artist_str.replace(" & ", "|").replace(", ", "|").replace(",", "|").replace(";", "|")
        # Split and strip whitespace, convert to lowercase for case-insensitive comparison
        artists = {name.strip().lower() for name in normalized.split("|") if name.strip()}
        return artists
    
    old_artists = normalize_artists(old_artist_str)
    new_artists = normalize_artists(new_artist_str)
    
    # Artists match if both sets contain the same names
    return old_artists == new_artists


def print_changes(album_changes, track_changes, a_track):
    """Print all the proposed track changes. Album-level tags are no longer modified on files."""
    if any(t for t in track_changes.values()):
        click.secho("\nProposed tag changes (updating artists to match scraped metadata):", fg="yellow", bold=True)
        for filename, changes in track_changes.items():
            if changes:
                click.secho(f"> {filename}", fg="yellow")
                for change in changes:
                    click.echo(f"  {change.tag.ljust(20)} ••• {change.old} {ARROWS} {change.new}")


def retag_files(path, album_changes, track_changes, preserve_artists=False):
    """Apply the proposed metadata changes to the files.
    
    Note: album_changes is now empty - we only tag artist info, updating to match scraped metadata.
    """
    # Only save files if there are actual changes
    files_changed = 0
    for filename, changes in track_changes.items():
        if changes:  # Only process files with changes
            mut = TagFile(os.path.join(path, filename))
            for change in changes:
                setattr(mut, change.tag, str(change.new))
            mut.save()
            files_changed += 1
    
    if files_changed > 0:
        click.secho(f"Retagged {files_changed} file(s) with correct artist tags from scraped metadata.", fg="green")


def rename_files(path, tags, metadata, auto_rename, spectral_ids, source=None):
    """
    Call functions that generate the proposed changes, then print and prompt
    for confirmation. Apply the changes if user agrees.
    """
    to_rename = []
    folders_to_create = set()
    multi_disc = len(metadata["tracks"]) > 1
    md_word = "CD"  # "Disc" if source == "CD" else "Part"

    track_list = list(chain.from_iterable([d.values() for d in metadata["tracks"].values()]))
    multiple_artists = any(
        {a for a, i in t["artists"] if i == "main"} != {a for a, i in track_list[0]["artists"] if i == "main"}
        for t in track_list[1:]
    )

    for filename, tracktags in tags.items():
        ext = os.path.splitext(filename)[1].lower()
        new_name = generate_file_name(tracktags, ext, multiple_artists)
        if multi_disc:
            if isinstance(tracktags, dict):
                disc_number = int(tracktags["discnumber"][0].split("/")[0]) if "discnumber" in tracktags else 1
            else:
                disc_number = int(tracktags.discnumber.split("/")[0]) or 1
            new_name = os.path.join(f"{md_word}{disc_number:02d}", new_name)
        if filename != new_name:
            to_rename.append((filename, new_name))
            if multi_disc:
                folders_to_create.add(os.path.join(path, f"{md_word}{disc_number:02d}"))

    if to_rename:
        print_filenames(to_rename)
        if auto_rename or click.confirm(
            click.style("\nWould you like to rename the files?", fg="magenta"),
            default=True,
        ):
            for folder in folders_to_create:
                if not os.path.isdir(folder):
                    os.mkdir(folder)
            directory_move_pairs = set()
            for filename, new_name in to_rename:
                old_dir = os.path.dirname(os.path.join(path, filename))
                new_dir = os.path.dirname(os.path.join(path, new_name))

                if old_dir != path:
                    directory_move_pairs.add((os.path.splitext(filename)[1], old_dir, new_dir))
                new_path, new_path_ext = os.path.splitext(os.path.join(path, new_name))
                # new_path = new_path[: 200 - len(new_path_ext) + len(os.path.dirname(path))] + new_path_ext
                new_path = new_path + new_path_ext
                os.rename(os.path.join(path, filename), new_path)

                # Update spectral_ids with new filenames, if spectrals were generated
                if spectral_ids:
                    for old_name, new_name in to_rename:
                        for key, value in spectral_ids.items():
                            if value == old_name:
                                spectral_ids[key] = new_name

            move_non_audio_files(directory_move_pairs)
            delete_empty_folders(path)
    else:
        click.secho("\nNo file renaming is recommended.", fg="green")


def print_filenames(to_rename):
    """Print all the proposed filename changes."""
    click.secho("\nProposed filename changes:", fg="yellow", bold=True)
    for filename, new_name in to_rename:
        click.echo(f"   {filename} {ARROWS} {new_name}")


def generate_file_name(tags, ext, multiple_artists, trackno_or=None):
    """Generate the template keys and format the template with the tags."""
    template = cfg.upload.formatting.file_template
    keys = [fn for _, fn, _, _ in Formatter().parse(template) if fn]
    if (
        "artist" in keys
        and cfg.upload.formatting.no_artist_in_filename_if_only_one_album_artist
        and not multiple_artists
    ):
        keys.remove("artist")
        template = cfg.upload.formatting.one_album_artist_file_template
    if isinstance(tags, dict):
        template_keys = {k: _parse_integer(tags[k][0]) for k in keys}
    else:
        template_keys = {}
        for k in keys:
            val = _parse_integer(getattr(tags, k))
            if k == "artist":
                val = val[0]
            template_keys[k] = val

    if "artist" in keys:
        if isinstance(tags, dict):
            artist_count = str(tags["artist"]).count(",") + str(tags["artist"]).count("&")
        else:
            artist_count = str(tags.artist).count(",") + str(tags.artist).count("&")
        if artist_count > cfg.upload.formatting.various_artist_threshold:
            template_keys["artist"] = cfg.upload.formatting.various_artist_word
    if "tracknumber" in keys and trackno_or is not None:
        template_keys["tracknumber"] = trackno_or
    new_base = template.format(**template_keys) + ext
    if cfg.upload.description.fullwidth_replacements:
        for char, sub in BLACKLISTED_FULLWIDTH_REPLACEMENTS.items():
            new_base = new_base.replace(char, sub)
    return re.sub(BLACKLISTED_CHARS, cfg.upload.formatting.blacklisted_substitution, new_base)


def _parse_integer(value):
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        return f"{int(value):02d}"
    return value


def move_non_audio_files(directory_move_pairs):
    for ext, old_dir, new_dir in directory_move_pairs:
        for figle in os.listdir(old_dir):
            if not figle.endswith(ext) or os.path.isdir(os.path.join(old_dir, figle)):
                shutil.move(os.path.join(old_dir, figle), os.path.join(new_dir, figle))


def delete_empty_folders(path):
    for root, dirs, files in os.walk(path):
        if not dirs and not files:
            os.rmdir(root)
