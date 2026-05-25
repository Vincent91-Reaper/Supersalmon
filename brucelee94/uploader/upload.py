import asyncio
import os

import click
from torf import Torrent

from brucelee94 import cfg
from brucelee94.common import str_to_int_if_int
from brucelee94.constants import ARTIST_IMPORTANCES
from brucelee94.errors import RequestError
# Source icons and metasources removed (no longer used in descriptions)
# from brucelee94.sources import SOURCE_ICONS
# from brucelee94.tagger.sources import METASOURCES
# Spectral imports removed
# from salmon.uploader.spectrals import (
#     make_spectral_bbcode,
# )


def _get_event_loop():
    """Get or create an event loop for async operations."""
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop


def _tag_number_prefix(value, default=None):
    """Return the first numeric part of a tag number stored as int or '1/2'."""
    if value is None or value == "":
        return default
    return str(value).split("/")[0]


def _is_later_disc(value):
    """Return True when a discnumber tag indicates disc 2 or later."""
    disc_num = _tag_number_prefix(value)
    if not disc_num:
        return False
    try:
        return int(disc_num) > 1
    except (TypeError, ValueError):
        return False


def prepare_and_upload(
    gazelle_site,
    path,
    group_id,
    metadata,
    cover_url,
    track_data,
    hybrid,
    # lossy_master,  # removed
    # spectral_urls,  # removed
    # spectral_ids,  # removed
    # lossy_comment,  # removed
    # request_id,  # removed
    source_url=None,
    override_description=None,
):
    """Wrapper function for all the data compiling and processing."""
    if not group_id:
        data = compile_data_new_group(
            gazelle_site,
            path,
            metadata,
            track_data,
            hybrid,
            cover_url,
            # spectral_urls,  # removed
            # spectral_ids,  # removed
            # lossy_comment,  # removed
            # request_id,  # removed
            source_url=source_url,
        )
    else:
        data = compile_data_existing_group(
            gazelle_site,
            path,
            group_id,
            metadata,
            track_data,
            hybrid,
            # spectral_urls,  # removed
            # spectral_ids,  # removed
            # lossy_comment,  # removed
            # request_id,  # removed
            source_url=source_url,
            override_description=override_description,
        )
    torrent_path, torrent_content = generate_torrent(gazelle_site, path)
    files = compile_files(path, torrent_path, metadata)

    click.secho("Uploading torrent...", fg="yellow")
    try:
        loop = _get_event_loop()
        torrent_id, group_id, newgroup = loop.run_until_complete(gazelle_site.upload(data, files))
        return torrent_id, group_id, torrent_path, torrent_content, newgroup
    except RequestError as e:
        click.secho(str(e), fg="red", bold=True)
        exit()


def concat_track_data(tags, audio_info):
    """Combine the tag and audio data into one dictionary per track."""
    track_data = {}
    for k, v in audio_info.items():
        track_data[k] = {**v, "t": tags[k]}
    return track_data


def compile_data_new_group(
    gazelle_site,
    path,
    metadata,
    track_data,
    hybrid,
    cover_url,
    # spectral_urls,  # removed
    # spectral_ids,  # removed
    # lossy_comment,  # removed
    # request_id=None,  # removed
    source_url=None,
):
    """
    Compile the data dictionary that needs to be submitted with a brand new
    torrent group upload POST.
    
    NOTE: Label and catalog are torrent-specific (remaster fields), not group-level.
    Each torrent in a group can have different label/catalog.
    """
    # Ensure DJ Mix is properly mapped, with fallback to Album if key doesn't exist
    rls_type_id = gazelle_site.release_types.get(metadata["rls_type"])
    if rls_type_id is None:
        click.secho(f"WARNING: Release type '{metadata['rls_type']}' not found in tracker release types. Defaulting to Album.", fg="red")
        rls_type_id = gazelle_site.release_types.get("Album", 1)
    
    # For DJ Mix releases, use empty label (Apple Music doesn't provide proper label info)
    if metadata.get("rls_type") == "DJ Mix":
        record_label = ""
    else:
        record_label = metadata.get("label", "")
    
    data = {
        "submit": True,
        "type": 0,
        "title": metadata["title"],
        "artists[]": [a[0] for a in metadata["artists"]],
        "importance[]": [ARTIST_IMPORTANCES[a[1]] for a in metadata["artists"]],
        "year": metadata["group_year"],
        "record_label": record_label,  # Group-level label (empty for DJ Mix)
        "catalogue_number": generate_catno(metadata),  # Group-level catalog
        "releasetype": rls_type_id,
        "remaster": True,
        "remaster_year": metadata["year"],
        "remaster_title": metadata["edition_title"],
        "remaster_record_label": "",  # Defer to post-upload update
        "remaster_catalogue_number": "",  # Defer to post-upload update
        "format": metadata["format"],
        "bitrate": metadata["encoding"],
        "other_bitrate": None,
        **({"scene": metadata["scene"]} if metadata.get("scene") else {}),
        "vbr": metadata["encoding_vbr"],
        "media": metadata["source"],
        "tags": metadata["tags"],
        "album_desc": generate_description(track_data, metadata),
        "release_desc": generate_t_description(
            metadata, track_data, hybrid, metadata["urls"], source_url  # spectral params removed
        ),
        # "requestid": request_id,  # removed
    }
    # Only include image if cover_url is provided (not None)
    if cover_url:
        data["image"] = cover_url
    return data


def compile_data_existing_group(
    gazelle_site,
    path,
    group_id,
    metadata,
    track_data,
    hybrid,
    # spectral_urls,  # removed
    # spectral_ids,  # removed
    # lossy_comment,  # removed
    # request_id,  # removed
    source_url=None,
    override_description=None,
):
    """Compile the data that needs to be submitted
    with an upload to an existing group.
    
    NOTE: Label and catalog are torrent-specific (remaster fields), not group-level.
    Each torrent in a group can have different label/catalog.
    """
    return {
        "submit": True,
        "type": 0,
        "groupid": group_id,
        "remaster": True,
        "remaster_year": metadata["year"],
        "remaster_title": metadata["edition_title"],
        "remaster_record_label": "",  # Defer to post-upload update
        "remaster_catalogue_number": "",  # Defer to post-upload update
        "format": metadata["format"],
        "bitrate": metadata["encoding"],
        **({"scene": metadata["scene"]} if metadata.get("scene") else {}),
        "other_bitrate": None,
        "vbr": metadata["encoding_vbr"],
        "media": metadata["source"],
        "release_desc": override_description
        if override_description
        else generate_t_description(
            metadata, track_data, hybrid, metadata["urls"], source_url  # spectral params removed
        ),
        # "requestid": request_id,  # removed
    }


def compile_files(path, torrent_path, metadata):
    """
    Compile a list of file tuples that should be uploaded. This consists
    of the .torrent and any log files.
    """
    files = []
    with open(torrent_path, "rb") as torrent_file:
        files.append(("file_input", ("meowmeow.torrent", torrent_file.read(), "application/octet-stream")))
    if metadata["source"] == "CD":
        files += attach_logfiles(path)
    return files


def attach_logfiles(path):
    """Attach all the log files that should be uploaded."""
    logfiles = []
    for root, _, files in os.walk(path):
        for filename in files:
            if filename.lower().endswith(".log"):
                filepath = os.path.abspath(os.path.join(root, filename))
                with open(filepath, "rb") as f:
                    logfiles.append((filename, f.read(), "application/octet-stream"))
    return [("logfiles[]", lf) for lf in logfiles]


def generate_catno(metadata):
    if metadata.get("catno"):
        return metadata["catno"]
    elif cfg.upload.compression.use_upc_as_catno:
        return metadata.get("upc", "")
    return ""


def generate_torrent(gazelle_site, path):
    """Call the dottorrent function to generate a torrent."""
    click.secho("Generating torrent file...", fg="yellow", nl=False)
    t = Torrent(
        path,
        trackers=[gazelle_site.announce],
        private=True,
        source=gazelle_site.site_string,
    )
    t.generate()
    tpath = os.path.join(
        # tempfile.gettempdir(),
        gazelle_site.dot_torrents_dir,
        f"{os.path.basename(path)} - {gazelle_site.site_string}.torrent",
    )
    t.write(tpath, overwrite=True)
    click.secho(" done!", fg="yellow")
    return tpath, t


def all_tracks_have_same_artists(tracks, main_artists):
    """
    Check if all tracks have the same artist set as the album's main artists.
    Returns True only if every track has exactly the same artists.
    
    Used to determine if per-track artists should be shown:
    - If all tracks have same artists → Don't show (redundant)
    - If tracks have different artists → Show (needed for clarity)
    """
    if not tracks or not main_artists:
        return True
    
    # Normalize main artists for comparison (lowercase, strip whitespace)
    main_artists_normalized = {artist.lower().strip() for artist in main_artists}
    
    for track in tracks:
        # Get track artists from file tags
        track_artist = track['t'].artist if hasattr(track['t'], 'artist') else None
        if not track_artist:
            continue
            
        # Split and normalize track artists
        track_artists = set()
        
        # Handle both list and string formats
        if isinstance(track_artist, list):
            # Artist is already a list (e.g., from Beatport)
            for artist in track_artist:
                if artist and artist.strip():
                    track_artists.add(artist.strip().lower())
        else:
            # Artist is a string, needs splitting (e.g., from iTunes)
            for part in track_artist.split(', '):
                for artist in part.split(' & '):
                    if artist.strip():
                        track_artists.add(artist.strip().lower())
        
        # If this track's artists differ from main artists, tracks vary
        if track_artists != main_artists_normalized:
            return False
    
    return True


def add_artist_bbcode_to_feat(title):
    """
    Add [artist] BBCode tags to guest artists in (feat. ...) mentions within track title.
    
    Detects patterns like:
    - (feat. Name)
    - (ft. Name)
    - (featuring Name)
    
    And transforms them to:
    - (feat. [artist]Name[/artist])
    
    Handles multiple guests separated by ", " and " & "
    """
    import re
    
    # Pattern to match (feat. ...), (ft. ...), or (featuring ...)
    pattern = r'\((feat\.|ft\.|featuring)\s+([^)]+)\)'
    
    def add_bbcode_to_match(match):
        feat_keyword = match.group(1)  # "feat.", "ft.", or "featuring"
        guests_text = match.group(2)  # The guest names
        
        # Split guests on ", " and then on " & "
        guest_list = []
        for comma_part in guests_text.split(', '):
            for guest in comma_part.split(' & '):
                guest = guest.strip()
                if guest:
                    guest_list.append(guest)
        
        # Create BBCode version
        if len(guest_list) == 1:
            bbcode_guests = f"[artist]{guest_list[0]}[/artist]"
        elif len(guest_list) == 2:
            bbcode_guests = f"[artist]{guest_list[0]}[/artist] & [artist]{guest_list[1]}[/artist]"
        else:
            # Multiple guests: use ", " for all but last, " & " for last
            bbcode_guests = ', '.join([f"[artist]{g}[/artist]" for g in guest_list[:-1]])
            bbcode_guests += f" & [artist]{guest_list[-1]}[/artist]"
        
        return f"({feat_keyword} {bbcode_guests})"
    
    # Replace all feat. mentions with BBCode version
    return re.sub(pattern, add_bbcode_to_match, title, flags=re.IGNORECASE)


def format_track_artists(track_metadata):
    """
    Format track artists by separating main artists from guest/featured artists.
    Returns tuple: (main_artists_str, guest_artists_str)
    
    Example:
        If track has Jon Hansen (main) and Mary Doufle (guest):
        Returns: ("[artist]Jon Hansen[/artist]", "[artist]Mary Doufle[/artist]")
    """
    if not track_metadata or "artists" not in track_metadata:
        return "", ""
    
    main_artists = []
    guest_artists = []
    
    for artist_name, importance in track_metadata["artists"]:
        if importance == "main":
            main_artists.append(artist_name)
        elif importance == "guest":
            guest_artists.append(artist_name)
    
    # Format main artists with [artist] tags
    main_str = ""
    if main_artists:
        artist_tags = [f"[artist]{artist}[/artist]" for artist in main_artists]
        main_str = ", ".join(artist_tags)
    
    # Format guest artists with [artist] tags
    guest_str = ""
    if guest_artists:
        artist_tags = [f"[artist]{artist}[/artist]" for artist in guest_artists]
        guest_str = ", ".join(artist_tags)
    
    return main_str, guest_str


def generate_description(track_data, metadata):
    """Generate the group description with tracklist including per-track artists only for Various Artists albums."""
    # Generate header with artist and album title
    
    # For DJ Mix releases, use DJ/Compiler artist in header instead of main artists
    if metadata.get("rls_type") == "DJ Mix":
        dj_artists = [a for a, i in metadata["artists"] if i == "djcompiler"]
        if dj_artists:
            # Use DJ/Compiler artist(s) for DJ Mix releases
            if len(dj_artists) == 1:
                description = f"[b][artist]{dj_artists[0]}[/artist] - {metadata['title']}[/b]\n"
            else:
                # Multiple DJ/Compilers - use " & " separator
                artist_tags = [f"[artist]{artist}[/artist]" for artist in dj_artists]
                artist_display = " & ".join(artist_tags)
                description = f"[b]{artist_display} - {metadata['title']}[/b]\n"
            # DJ Mixes should show all performers, so mark as Various Artists
            is_various_artists = True
        else:
            # Fallback if no DJ/Compiler found (shouldn't happen for DJ Mix)
            main_artists = [a for a, i in metadata["artists"] if i == "main"]
            is_various_artists = len(main_artists) >= 3
            if is_various_artists:
                description = f"[b]Various Artists - {metadata['title']}[/b]\n"
            else:
                sorted_artists = sorted(main_artists)
                if len(sorted_artists) == 1:
                    description = f"[b][artist]{sorted_artists[0]}[/artist] - {metadata['title']}[/b]\n"
                else:
                    artist_tags = [f"[artist]{artist}[/artist]" for artist in sorted_artists]
                    artist_display = " & ".join(artist_tags)
                    description = f"[b]{artist_display} - {metadata['title']}[/b]\n"
    else:
        # Non-DJ Mix releases: use existing logic
        main_artists = [a for a, i in metadata["artists"] if i == "main"]
        # Use "Various Artists" for albums with 3+ main artists
        is_various_artists = len(main_artists) >= 3
        if is_various_artists:
            description = f"[b]Various Artists - {metadata['title']}[/b]\n"
        else:
            # Format each artist with individual [artist] tags inside [b] tags
            sorted_artists = sorted(main_artists)
            if len(sorted_artists) == 1:
                description = f"[b][artist]{sorted_artists[0]}[/artist] - {metadata['title']}[/b]\n"
            else:
                # Use " & " separator outside [artist] tags for 2 artists
                artist_tags = [f"[artist]{artist}[/artist]" for artist in sorted_artists]
                artist_display = " & ".join(artist_tags)
                description = f"[b]{artist_display} - {metadata['title']}[/b]\n"
    
    # Add release date if available (already formatted as "Month Day, Year")
    if metadata.get("date"):
        description += f"{metadata['date']}\n"
    
    description += "\n"
    
    # Check if multi-disc album
    multi_disc = any(
        (
            t["t"].discnumber
            and str(t["t"].discnumber) != "1/1"
            and (
                str(t["t"].discnumber).startswith("1/")
                or _is_later_disc(t["t"].discnumber)
            )
        )
        for t in track_data.values()
    )
    
    # Check if this is a DJ Mix release
    is_dj_mix = metadata.get("rls_type") == "DJ Mix"
    
    # Create a mapping from (disc, track) to metadata track for artist info
    # (Only used for non-DJ Mix releases)
    # metadata["tracks"] structure: {disc_num: {track_num: track_metadata}}
    # Note: Keys are stored as strings for consistent lookup with track numbers extracted from tags
    metadata_tracks_map = {}
    if not is_dj_mix and metadata.get("tracks"):
        for disc_num, disc_tracks in metadata["tracks"].items():
            for track_num, track_meta in disc_tracks.items():
                # Store using string keys for consistent lookup
                metadata_tracks_map[(str(disc_num), str(track_num))] = track_meta
    
    # Smart artist display logic for non-DJ Mix albums
    # DJ Mix always shows per-track artists (excluded from this logic)
    # For non-DJ Mix: Check if all tracks have the same artists
    show_track_artists = False
    if not is_dj_mix:
        # For single-artist albums, never show per-track artists (redundant)
        if len(main_artists) == 1:
            show_track_artists = False
        else:
            # For multi-artist albums, check if artists vary
            tracks_have_same_artists = all_tracks_have_same_artists(list(track_data.values()), main_artists)
            # Show per-track artists only if they vary across tracks
            show_track_artists = not tracks_have_same_artists
    
    total_duration = 0
    
    if multi_disc:
        # Group tracks by disc for multi-disc albums
        from collections import defaultdict
        tracks_by_disc = defaultdict(list)
        
        for track in track_data.values():
            disc_num = _tag_number_prefix(track["t"].discnumber, default="1")
            tracks_by_disc[disc_num].append(track)
        
        # Sort discs and tracks
        sorted_discs = sorted(tracks_by_disc.keys(), key=lambda x: int(x))
        
        for disc_num in sorted_discs:
            # Add disc header
            description += f"[size=2][b]Disc {disc_num}[/b][/size]\n"
            
            # Sort tracks within disc by track number
            disc_tracks = sorted(
                tracks_by_disc[disc_num],
                key=lambda t: int(_tag_number_prefix(t["t"].tracknumber, default="0")),
            )
            
            for track in disc_tracks:
                length = "{:02d}:{:02d}".format(track["duration"] // 60, track["duration"] % 60)
                total_duration += track["duration"]
                
                # Use original track number from metadata - extract just the number part if it contains "/"
                track_num_raw = _tag_number_prefix(track['t'].tracknumber, default="0")
                # Zero-pad track numbers
                track_num = str_to_int_if_int(track_num_raw, zpad=True)
                description += f"[b]{track_num}.[/b] "
                
                # For DJ Mix: Use file-based artists (no guest separation)
                # For non-DJ Mix: Use metadata-based artists with guest separation
                if is_dj_mix:
                    # DJ Mix: Read artist directly from file tags
                    if is_various_artists:
                        track_artist = track['t'].artist
                        if isinstance(track_artist, list):
                            # Split each artist on both ", " and " & " and create separate [artist] tags
                            all_artists = []
                            for artist in track_artist:
                                # Split on both ", " and " & " to separate combined artists
                                # e.g., "Alix Perez, Shades & Eprom" -> ["Alix Perez", "Shades", "Eprom"]
                                for comma_part in artist.split(', '):
                                    all_artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
                            artist_tags = [f"[artist]{artist}[/artist]" for artist in all_artists]
                            description += f"{', '.join(artist_tags)} - "
                        elif track_artist:
                            # Split single artist string on both ", " and " & "
                            artists = []
                            for comma_part in track_artist.split(', '):
                                artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
                            artist_tags = [f"[artist]{artist}[/artist]" for artist in artists]
                            description += f"{', '.join(artist_tags)} - "
                    
                    # Add inline BBCode to guest artists in title (if present)
                    title_with_bbcode = add_artist_bbcode_to_feat(track['t'].title)
                    description += f"{title_with_bbcode} [i]({length})[/i]\n"
                else:
                    # Non-DJ Mix: Use metadata-based artists with guest separation
                    # Get track metadata for artist info (if available)
                    disc_for_lookup = _tag_number_prefix(track['t'].discnumber, default="1")
                    
                    track_metadata = metadata_tracks_map.get((disc_for_lookup, track_num_raw))
                    
                    # Format artists: main before title, guest/featured after in (feat. ...)
                    if show_track_artists and track_metadata:
                        main_artists_str, guest_artists_str = format_track_artists(track_metadata)
                        
                        # Add main artists before the title
                        if main_artists_str:
                            description += f"{main_artists_str} - "
                        
                        # Add title
                        title = track['t'].title
                        
                        # Check if title already has inline guest artists
                        import re
                        title_has_inline_guests = re.search(r'\((feat\.|ft\.|featuring)', title, re.IGNORECASE)
                        
                        if title_has_inline_guests:
                            # Add BBCode to inline guests, don't append separate guest suffix
                            description += add_artist_bbcode_to_feat(title)
                        else:
                            # No inline guests in title
                            description += title
                            # Add guest/featured artists after title in (feat. ...)
                            if guest_artists_str:
                                description += f" (feat. {guest_artists_str})"
                        
                        description += f" [i]({length})[/i]\n"
                    else:
                        # Main artists don't vary, so don't show them per-track
                        # But still check for guest artists to display
                        title = track['t'].title
                        
                        # Check if title already has inline guest artists
                        import re
                        title_has_inline_guests = re.search(r'\((feat\.|ft\.|featuring)', title, re.IGNORECASE)
                        
                        if title_has_inline_guests:
                            # Add BBCode to inline guests
                            description += add_artist_bbcode_to_feat(title)
                        else:
                            # No inline guests in title
                            description += title
                            # Check metadata for guest artists and append if present
                            if track_metadata:
                                _, guest_artists_str = format_track_artists(track_metadata)
                                if guest_artists_str:
                                    description += f" (feat. {guest_artists_str})"
                        
                        description += f" [i]({length})[/i]\n"
            
            # Add blank line after each disc (except the last one)
            if disc_num != sorted_discs[-1]:
                description += "\n"
    else:
        # Single disc album - use simple numbering
        for track in track_data.values():
            length = "{:02d}:{:02d}".format(track["duration"] // 60, track["duration"] % 60)
            total_duration += track["duration"]
            
            track_num_raw = _tag_number_prefix(track['t'].tracknumber, default="0")
            # Zero-pad track numbers
            track_num = str_to_int_if_int(track_num_raw, zpad=True)
            description += f"[b]{track_num}.[/b] "
            
            # For DJ Mix: Use file-based artists (no guest separation)
            # For non-DJ Mix: Use metadata-based artists with guest separation
            if is_dj_mix:
                # DJ Mix: Read artist directly from file tags
                if is_various_artists:
                    track_artist = track['t'].artist
                    if isinstance(track_artist, list):
                        # Split each artist on both ", " and " & " and create separate [artist] tags
                        all_artists = []
                        for artist in track_artist:
                            # Split on both ", " and " & " to separate combined artists
                            # e.g., "Alix Perez, Shades & Eprom" -> ["Alix Perez", "Shades", "Eprom"]
                            for comma_part in artist.split(', '):
                                all_artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
                        artist_tags = [f"[artist]{artist}[/artist]" for artist in all_artists]
                        description += f"{', '.join(artist_tags)} - "
                    elif track_artist:
                        # Split single artist string on both ", " and " & "
                        artists = []
                        for comma_part in track_artist.split(', '):
                            artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
                        artist_tags = [f"[artist]{artist}[/artist]" for artist in artists]
                        description += f"{', '.join(artist_tags)} - "
                
                # Add inline BBCode to guest artists in title (if present)
                title_with_bbcode = add_artist_bbcode_to_feat(track['t'].title)
                description += f"{title_with_bbcode} [i]({length})[/i]\n"
            else:
                # Non-DJ Mix: Use metadata-based artists with guest separation
                # Get track metadata for artist info (if available)
                # For single disc, use disc "1"
                track_metadata = metadata_tracks_map.get(("1", track_num_raw))
                
                # Format artists: main before title, guest/featured after in (feat. ...)
                if show_track_artists and track_metadata:
                    main_artists_str, guest_artists_str = format_track_artists(track_metadata)
                    
                    # Add main artists before the title
                    if main_artists_str:
                        description += f"{main_artists_str} - "
                    
                    # Add title
                    title = track['t'].title
                    
                    # Check if title already has inline guest artists
                    import re
                    title_has_inline_guests = re.search(r'\((feat\.|ft\.|featuring)', title, re.IGNORECASE)
                    
                    if title_has_inline_guests:
                        # Add BBCode to inline guests, don't append separate guest suffix
                        description += add_artist_bbcode_to_feat(title)
                    else:
                        # No inline guests in title
                        description += title
                        # Add guest/featured artists after title in (feat. ...)
                        if guest_artists_str:
                            description += f" (feat. {guest_artists_str})"
                    
                    description += f" [i]({length})[/i]\n"
                else:
                    # Main artists don't vary, so don't show them per-track
                    # But still check for guest artists to display
                    title = track['t'].title
                    
                    # Check if title already has inline guest artists
                    import re
                    title_has_inline_guests = re.search(r'\((feat\.|ft\.|featuring)', title, re.IGNORECASE)
                    
                    if title_has_inline_guests:
                        # Add BBCode to inline guests
                        description += add_artist_bbcode_to_feat(title)
                    else:
                        # No inline guests in title
                        description += title
                        # Check metadata for guest artists and append if present
                        if track_metadata:
                            _, guest_artists_str = format_track_artists(track_metadata)
                            if guest_artists_str:
                                description += f" (feat. {guest_artists_str})"
                    
                    description += f" [i]({length})[/i]\n"

    # Format total length
    if len(track_data.values()) > 1:
        if total_duration >= 3600:  # 1 hour or more
            hours = total_duration // 3600
            minutes = (total_duration % 3600) // 60
            seconds = total_duration % 60
            description += f"\n[b]Total length:[/b] {hours}:{minutes:02d}:{seconds:02d}\n"
        else:
            description += f"\n[b]Total length:[/b] {total_duration // 60}:{total_duration % 60:02d}\n"

    if metadata["comment"]:
        description += f"\n{metadata['comment']}\n"

    return description


def generate_t_description(
    metadata, track_data, hybrid, metadata_urls, source_url  # spectral params removed
):
    """
    Generate the torrent description. Only print bitrates and bit depth.
    Icons, images, release date, source links, and more info have been removed.
    """
    description = ""

    if not hybrid:
        track = next(iter(track_data.values()))
        if track["precision"]:
            description += "[b]{} bit [color=#2E86C1]{:.01f}[/color] kHz[/b]".format(
                track["precision"], track["sample rate"] / 1000
            )
            description += "\n"
        else:
            description += "{:.01f} kHz\n".format(track["sample rate"] / 1000)

    if cfg.upload.description.include_tracklist_in_t_desc or hybrid:
        for filename, track in track_data.items():
            description += os.path.splitext(filename)[0]
            description += " [i]({})[/i]".format(f"{track['duration'] // 60}:{track['duration'] % 60:02d}")
            if cfg.upload.description.bitrates_in_t_desc:
                description += " [{:.01f}kbps]".format(track["bit rate"] / 1000)

            if hybrid:
                description += " [{} bit / {} kHz]".format(track["precision"], track["sample rate"] / 1000)

            description += "\n"

    return description
