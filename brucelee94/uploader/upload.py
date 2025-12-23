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
        torrent_id, group_id = loop.run_until_complete(gazelle_site.upload(data, files))
        return torrent_id, group_id, torrent_path, torrent_content
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
    """
    return {
        "submit": True,
        "type": 0,
        "title": metadata["title"],
        "artists[]": [a[0] for a in metadata["artists"]],
        "importance[]": [ARTIST_IMPORTANCES[a[1]] for a in metadata["artists"]],
        "year": metadata["group_year"],
        "record_label": metadata["label"],
        "catalogue_number": generate_catno(metadata),
        "releasetype": gazelle_site.release_types[metadata["rls_type"]],
        "remaster": True,
        "remaster_year": metadata["year"],
        "remaster_title": metadata["edition_title"],
        "remaster_record_label": metadata["label"],
        "remaster_catalogue_number": generate_catno(metadata),
        "format": metadata["format"],
        "bitrate": metadata["encoding"],
        "other_bitrate": None,
        **({"scene": metadata["scene"]} if metadata.get("scene") else {}),
        "vbr": metadata["encoding_vbr"],
        "media": metadata["source"],
        "tags": metadata["tags"],
        "image": cover_url,
        "album_desc": generate_description(track_data, metadata),
        "release_desc": generate_t_description(
            metadata, track_data, hybrid, metadata["urls"], source_url  # spectral params removed
        ),
        # "requestid": request_id,  # removed
    }


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
    with an upload to an existing group."""
    return {
        "submit": True,
        "type": 0,
        "groupid": group_id,
        "remaster": True,
        "remaster_year": metadata["year"],
        "remaster_title": metadata["edition_title"],
        "remaster_record_label": metadata["label"],
        "remaster_catalogue_number": generate_catno(metadata),
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


def generate_description(track_data, metadata):
    """Generate the group description with the tracklist.
    Shows album header with main artist and title, then track numbers and titles."""
    # Get main artists for the header
    main_artists = [a[0] for a, i in metadata.get("artists", []) if i == "main"]
    if main_artists:
        # Format main artists
        if len(main_artists) > 2 and "&" not in "".join(main_artists):
            artist_str = ", ".join(main_artists)
        else:
            artist_str = " & ".join(main_artists)
    else:
        # Fallback to all artists if no main artists
        artist_str = " & ".join([a[0] for a in metadata.get("artists", [])])
    
    # Create header with artist and album title
    description = f"[b][Artist]{artist_str}[/artist] - {metadata.get('title', 'Unknown Album')}[/b]\n\n"
    
    multi_disc = any(
        (
            t["t"].discnumber
            and t["t"].discnumber != "1/1"
            and (t["t"].discnumber.startswith("1/") or int(t["t"].discnumber) > 1)
        )
        for t in track_data.values()
    )
    total_duration = 0
    for track in track_data.values():
        length = "{}:{:02d}".format(track["duration"] // 60, track["duration"] % 60)
        total_duration += track["duration"]
        if multi_disc:
            description += (
                f"[b]{str_to_int_if_int(track['t'].discnumber, zpad=True)}-"
                f"{str_to_int_if_int(track['t'].tracknumber, zpad=True)}.[/b] "
            )
        else:
            description += f"[b]{str_to_int_if_int(track['t'].tracknumber, zpad=True)}.[/b] "

        # Show only track title without artist information
        description += f"{track['t'].title} [i]({length})[/i]\n"

    if len(track_data.values()) > 1:
        description += f"\n[b]Total length: [/b]{total_duration // 60}:{total_duration % 60:02d}\n"

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
