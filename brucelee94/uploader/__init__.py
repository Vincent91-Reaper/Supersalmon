import asyncio
import os
import platform
import re
import shutil

import click
import pyperclip

import brucelee94.trackers
from brucelee94 import cfg
# MQA checking removed
# from salmon.checks import mqa_test
# Integrity check removed
# from brucelee94.checks.integrity import (
#     check_integrity,
#     format_integrity,
#     sanitize_integrity,
# )
from brucelee94.checks.logs import check_log_cambia
# Upconvert check removed
# from brucelee94.checks.upconverts import upload_upconvert_test
from brucelee94.common import commandgroup
from brucelee94.constants import ENCODINGS, FORMATS, SOURCES, TAG_ENCODINGS
# Import downconversion functionality
from brucelee94.converter.downconverting import (
    convert_folder,
    generate_conversion_description,
)
from brucelee94.errors import AbortAndDeleteFolder, InvalidMetadataError
from brucelee94.images import upload_cover
from brucelee94.tagger import (
    metadata_validator_base,
    validate_encoding,
    validate_source,
)
from brucelee94.tagger.audio_info import (
    check_hybrid,
    gather_audio_info,
    recompress_path,
)
from brucelee94.tagger.cover import compress_pictures, download_cover_if_nonexistent
# Folder renaming removed
# from salmon.tagger.foldername import rename_folder
from brucelee94.tagger.folderstructure import check_folder_structure
from brucelee94.tagger.metadata import get_metadata
from brucelee94.tagger.pre_data import construct_rls_data
from brucelee94.tagger.retagger import tag_files  # rename_files removed
from brucelee94.tagger.review import review_metadata
from brucelee94.tagger.tags import check_tags, gather_tags, standardize_tags
from brucelee94.uploader.upload_to_group import (
    check_existing_group,
    print_torrents,
)
from brucelee94.uploader.preassumptions import print_preassumptions
# Request filling removed
# from salmon.uploader.request_checker import check_requests
from brucelee94.uploader.seedbox import UploadManager
# Spectral generation/upload removed
# from salmon.uploader.spectrals import (
#     check_spectrals,
#     generate_lossy_approval_comment,
#     get_spectrals_path,
#     handle_spectrals_upload_and_deletion,
#     post_upload_spectral_check,
#     report_lossy_master,
# )
from brucelee94.uploader.upload import (
    concat_track_data,
    prepare_and_upload,
)

loop = asyncio.get_event_loop()


@commandgroup.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--group-id", "-g", default=None, help="Group ID to upload torrent to")
@click.option(
    "--source",
    "-s",
    type=click.STRING,
    callback=validate_source,
    help=f"Source of files ({'/'.join(SOURCES.values())})",
)
# Lossy master option removed
# @click.option(
#     "--lossy/--not-lossy",
#     "-l/-L",
#     default=None,
#     help="Whether or not the files are lossy mastered",
# )
# Spectral options removed
# @click.option(
#     "--spectrals",
#     "-sp",
#     type=click.INT,
#     multiple=True,
#     help="Track numbers of spectrals to include in torrent description",
# )
@click.option(
    "--overwrite",
    "-ow",
    is_flag=True,
    help="Whether or not to use the original metadata.",
)
@click.option(
    "--encoding",
    "-e",
    type=click.STRING,
    callback=validate_encoding,
    help="You must specify one of the following encodings if files aren't lossless: "
    + ", ".join(list(TAG_ENCODINGS.keys())),
)
@click.option(
    "--compress",
    "-c",
    is_flag=True,
    help="Recompress flacs to the configured compression level before uploading.",
)
@click.option(
    "--tracker",
    "-t",
    callback=brucelee94.trackers.validate_tracker,
    help=f"Uploading Choices: ({'/'.join(brucelee94.trackers.tracker_list)})",
)
# Request filling removed
# @click.option("--request", "-r", default=None, help="Pass a request URL or ID")
# Spectral after option removed
# @click.option(
#     "--spectrals-after",
#     "-a",
#     is_flag=True,
#     help="Assess / upload / report spectrals after torrent upload",
# )
# File/folder renaming option removed
# @click.option(
#     "--auto-rename",
#     "-n",
#     is_flag=True,
#     help="Rename files and folders automatically",
# )
# Upconvert check option removed
# @click.option(
#     "--skip-up",
#     is_flag=True,
#     help="Skip check for 24 bit upconversion",
# )
@click.option("--scene", is_flag=True, help="Is this a scene release (default: False)")
@click.option(
    "--source-url",
    "-su",
    default=None,
    help="For WEB uploads provide the source of the album to be added in release description",
)
@click.option("-yyy", is_flag=True, help="Automatically pick the default answer for prompt")
# MQA check option removed
# @click.option(
#     "--skip-mqa",
#     is_flag=True,
#     help="Skip check for MQA marker (on first file only)",
# )
@click.option(
    "--skip-log-check",
    is_flag=True,
    help="Skip checking CD logs",
)
# Integrity check option removed
# @click.option(
#     "--skip-integrity-check",
#     is_flag=True,
#     help="Skip integrity check of audio files",
# )
def up(
    path,
    group_id,
    source,
    # lossy,  # removed
    # spectrals,  # removed
    overwrite,
    encoding,
    compress,
    tracker,
    # request,  # removed
    # spectrals_after,  # removed
    # auto_rename,  # removed
    # skip_up,  # removed
    scene,
    source_url,
    yyy,
    # skip_mqa,  # removed
    skip_log_check,
    # skip_integrity_check,  # removed
):
    """Command to upload an album folder to a Gazelle Site."""
    if yyy:
        cfg.upload.yes_all = True
    gazelle_site = brucelee94.trackers.get_class(tracker)()
    # Request filling removed
    # if request:
    #     request = brucelee94.trackers.validate_request(gazelle_site, request)
    #     # This is isn't handled by click because we need the tracker sorted first.
    print_preassumptions(
        gazelle_site,
        path,
        group_id,
        source,
        # lossy,  # removed
        # spectrals,  # removed
        encoding,
        # spectrals_after,  # removed
    )
    if source_url:
        source_url = source_url.strip()
    upload(
        gazelle_site,
        path,
        group_id,
        source,
        # lossy,  # removed
        # spectrals,  # removed
        encoding,
        source_url=source_url,
        scene=scene,
        overwrite_meta=overwrite,
        recompress=compress,
        # request_id=request,  # removed
        # spectrals_after=spectrals_after,  # removed
        # auto_rename=auto_rename,  # removed
        # skip_up=skip_up,  # removed
        # skip_mqa=skip_mqa,  # removed
        skip_log_check=skip_log_check,
        # skip_integrity_check=skip_integrity_check,  # removed
    )


def upload(
    gazelle_site,
    path,
    group_id,
    source,
    # lossy,  # removed
    # spectrals,  # removed
    encoding,
    scene=False,
    overwrite_meta=False,
    recompress=False,
    source_url=None,
    searchstrs=None,
    # request_id=None,  # removed
    # spectrals_after=False,  # removed
    # auto_rename=False,  # removed
    # skip_up=False,  # removed
    # skip_mqa=False,  # removed
    skip_log_check=False,
    # skip_integrity_check=False,  # removed
    is_16bit_transcode=False,  # NEW: Flag to indicate this is a 16-bit downconversion
    transcode_metadata=None,  # NEW: Metadata from the original 24-bit upload
):
    """Upload an album folder to RED (Gazelle Site)
    Multi-tracker upload removed."""
    path = os.path.abspath(path)
    remove_downloaded_cover_image = scene or cfg.image.remove_auto_downloaded_cover_image
    if not source:
        source = _prompt_source()
    audio_info = gather_audio_info(path)
    hybrid = check_hybrid(audio_info)
    if not scene:
        standardize_tags(path)
    tags = gather_tags(path)
    rls_data = construct_rls_data(
        tags,
        audio_info,
        source,
        encoding,
        scene=scene,
        overwrite=overwrite_meta,
        prompt_encoding=True,
        hybrid=hybrid,
    )

    try:
        # MQA checking removed
        # if not skip_mqa:
        #     click.secho("Checking for MQA release (first file only)", fg="cyan", bold=True)
        #     mqa_test(path)
        #     click.secho("No MQA release detected", fg="green")

        # Upconvert check removed
        # if rls_data["encoding"] == "24bit Lossless" and not skip_up:
        #     if not cfg.upload.yes_all:
        #         if click.confirm(
        #             click.style("\n24bit detected. Do you want to check whether might be upconverted?", fg="magenta"),
        #             default=True,
        #         ):
        #             upload_upconvert_test(path)
        #     else:
        #         upload_upconvert_test(path)

        if source == "CD" and not skip_log_check:
            click.secho("\nChecking logs", fg="green")
            for root, _, files in os.walk(path):
                for f in files:
                    if f.lower().endswith(".log"):
                        filepath = os.path.join(root, f)
                        click.secho(f"\nScoring {filepath}...", fg="cyan", bold=True)
                        try:
                            check_log_cambia(filepath, path)
                        except Exception as e:
                            if "Edited logs" in str(e):
                                raise click.Abort() from e
                            elif "CRC Mismatch" in str(e):
                                click.secho("Error: CRC mismatch between log and audio files!", fg="red", bold=True)
                                if not click.confirm(
                                    click.style(
                                        "Log file CRC does not match audio files. "
                                        "Do you want to continue upload anyway?",
                                        fg="magenta",
                                    ),
                                    default=False,
                                ):
                                    raise click.Abort() from e
                            else:
                                click.secho(f"Error checking log: {e}", fg="red")

        if group_id is None:
            # Dupe checking removed - just prompt for group selection
            group_id = check_existing_group(gazelle_site)

        # Spectral and lossy checking removed

        # For 16-bit transcodes, skip metadata scraping and retagging
        if is_16bit_transcode:
            # Skip get_metadata and edit_metadata - files are already properly tagged
            # Use metadata from the original 24-bit upload
            click.secho("16-bit transcode detected - using metadata from 24-bit upload", fg="cyan")
            
            if transcode_metadata is None:
                click.secho("ERROR: No metadata provided for 16-bit transcode upload!", fg="red", bold=True)
                raise click.Abort()
            
            # Use the metadata from the 24-bit upload, but update format/encoding from the 16-bit files
            metadata = transcode_metadata.copy()
            metadata["format"] = rls_data["format"]
            metadata["encoding"] = rls_data["encoding"]
            metadata["encoding_vbr"] = rls_data["encoding_vbr"]
            metadata["scene"] = rls_data["scene"]
            metadata["source"] = rls_data["source"]
            metadata["cover"] = None  # Will use cover.jpg from folder
        else:
            # Normal workflow: scrape metadata and retag
            metadata, new_source_url = get_metadata(path, tags, rls_data, provided_source_url=source_url)
            if new_source_url is not None:
                source_url = new_source_url
            
            # Special case: Tidal URLs - extract metadata from file tags instead of scraping
            if metadata.get("_extract_from_files"):
                click.secho("Extracting metadata from file tags...", fg="cyan")
                source_url = metadata.get("_source_url")
                
                # Build metadata from file tags
                metadata = _build_metadata_from_files(path, tags, rls_data)
                
                # Skip retagging for Tidal - files are already correct
                click.secho("Skipping file retagging for Tidal URL", fg="cyan")
                
                # Skip the edit_metadata workflow entirely for Tidal
                # Just check tags and folder structure
                tags = check_tags(path)
                if recompress:
                    recompress_path(path)
                check_folder_structure(path, metadata["scene"])
                
                # Refresh tags and audio info
                tags = gather_tags(path)
                audio_info = gather_audio_info(path)
            else:
                # Normal workflow for other sources
                # Copy format and encoding from rls_data to metadata (these come from audio files)
                metadata["format"] = rls_data["format"]
                metadata["encoding"] = rls_data["encoding"]
                metadata["encoding_vbr"] = rls_data["encoding_vbr"]
                metadata["scene"] = rls_data["scene"]
                metadata["source"] = rls_data["source"]
                
                # Detect if this is Apple Music URL (case-insensitive)
                is_apple_music = source_url and "apple.com" in source_url.lower()
                
                # Pass Apple Music flag to edit_metadata
                metadata["_is_apple_music"] = is_apple_music
                
                path, metadata, tags, audio_info = edit_metadata(
                    path, tags, metadata, source, rls_data, recompress, source_url, is_apple_music
                )

        if not group_id:
            # Dupe recheck removed - directly proceed
            click.echo()
        track_data = concat_track_data(tags, audio_info)
    except click.Abort:
        return click.secho("\nAborting upload...", fg="red")
    except AbortAndDeleteFolder:
        if platform.system() == "Windows" and cfg.upload.windows_use_recycle_bin:
            try:
                import send2trash

                send2trash.send2trash(path)
                return click.secho("\nMoved folder to recycle bin, aborting upload...", fg="red")
            except Exception as e:
                click.secho(f"\nError moving folder to recycle bin: {e}", fg="red")
                return click.secho("\nAborting upload...", fg="red")
        else:
            shutil.rmtree(path)
            return click.secho("\nDeleted folder, aborting upload...", fg="red")

    # Spectral and lossy master handling removed
    # lossy_comment = None
    # if spectrals_after:
    #     spectral_urls = None
    # else:
    #     if lossy_master:
    #         lossy_comment = generate_lossy_approval_comment(source_url, list(track_data.keys()))
    #         click.echo()
    #
    #     spectrals_path = get_spectrals_path(path)
    #     spectral_urls = handle_spectrals_upload_and_deletion(spectrals_path, spectral_ids)
    # Last minute dupe check removed (related to requests)
    # if cfg.upload.requests.last_minute_dupe_check:
    #     last_min_dupe_check(gazelle_site, searchstrs)

    # Multi-tracker upload removed - only upload to RED
    torrent_id = None
    cover_url = None

    seedbox_uploader = UploadManager()

    # Single upload to RED only (multi-tracker loop removed)
    # while True:
    #     # Loop until we don't want to upload to any more sites.
    #     if not tracker:
    #         if spectrals_after and torrent_id:
    #             # Here we are checking the spectrals after uploading to the first site
    #             # if they were not done before.
    #             lossy_master, lossy_comment, spectral_urls, spectral_ids = post_upload_spectral_check(
    #                 gazelle_site, path, torrent_id, None, track_data, source, source_url, format=rls_data["format"]
    #             )
    #             spectrals_after = False
    #         click.secho("\nWould you like to upload to another tracker? ", fg="magenta", nl=False)
    #         tracker = brucelee94.trackers.choose_tracker(remaining_gazelle_sites)
    #         if not tracker:
    #             click.secho("\nDone with this release.", fg="green")
    #             break
    #         gazelle_site = brucelee94.trackers.get_class(tracker)()
    #
    #         click.secho(f"Uploading to {gazelle_site.base_url}", fg="cyan", bold=True)
    #         searchstrs = generate_dupe_check_searchstrs(rls_data["artists"], rls_data["title"], rls_data["catno"])
    #         group_id = check_existing_group(gazelle_site, searchstrs, metadata)
    #
    #     remaining_gazelle_sites.remove(tracker)

    # Handle cover image
    if is_16bit_transcode:
        # For 16-bit transcodes, skip uploading cover to ptpimg entirely
        # The cover.jpg was already copied to the folder during downconversion
        # RED will use the local cover.jpg file from the torrent
        cover_url = None
        cover_path = os.path.join(path, "cover.jpg")
        if os.path.exists(cover_path):
            click.secho("Skipping cover upload to ptpimg for 16-bit transcode (using local cover.jpg)", fg="cyan")
        else:
            click.secho("Warning: cover.jpg not found in 16-bit folder", fg="yellow")
    elif group_id:
        if not remove_downloaded_cover_image:
            download_cover_if_nonexistent(path, metadata["cover"])
        # Don't need cover URL for existing groups
        cover_url = None
    else:
        # For new groups, we need a cover URL
        cover_path, is_downloaded = download_cover_if_nonexistent(path, metadata["cover"])
        cover_url = upload_cover(cover_path)
        if is_downloaded and remove_downloaded_cover_image:
            click.secho("Removing downloaded Cover Image File", fg="yellow")
            os.remove(cover_path)

    if not scene and cfg.image.auto_compress_cover:
        compress_pictures(path)

    # Request filling removed
    # if not request_id and cfg.upload.requests.check_requests:
    #     request_id = check_requests(gazelle_site, searchstrs)

    torrent_id, group_id, torrent_path, torrent_content, url = upload_and_report(
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
        source_url,
        seedbox_uploader,
        source=source,
    )

    # request_id = None  # removed

    torrent_content.comment = url
    torrent_content.write(torrent_path, overwrite=True)

    print_torrents(gazelle_site, group_id, highlight_torrent_id=torrent_id)

    # Check if 24-bit and prompt for downconversion to 16-bit
    if rls_data["encoding"] == "24bit Lossless":
        if click.confirm(click.style("\nDown-convert to 16-bit?", fg="magenta"), default=True):
            try:
                click.secho("\nStarting 24-bit to 16-bit downconversion...", fg="cyan", bold=True)
                
                # Perform downconversion
                final_sample_rate, new_path = convert_folder(path, bit_depth=16, sample_rate=None)
                
                click.secho(f"\n16-bit version created at: {new_path}", fg="green")
                click.secho("Uploading 16-bit version...\n", fg="cyan", bold=True)
                
                # Upload the 16-bit version with streamlined workflow
                # Skip metadata scraping, retagging, and cover upload (files are already tagged from 24-bit)
                # Pass the metadata from the 24-bit upload to avoid re-scraping
                upload(
                    gazelle_site,
                    new_path,
                    None,  # Upload as a new group (not to the existing group)
                    source,
                    encoding=None,  # Let it auto-detect as 16-bit
                    scene=scene,
                    overwrite_meta=overwrite_meta,
                    recompress=recompress,
                    source_url=source_url,  # Use the same source URL (Tidal/Apple Music/etc.) as the 24-bit version
                    searchstrs=searchstrs,
                    skip_log_check=skip_log_check,
                    is_16bit_transcode=True,  # NEW: Flag to skip metadata scraping/retagging/cover upload
                    transcode_metadata=metadata,  # Pass the metadata from the 24-bit upload
                )
                
            except Exception as e:
                click.secho(f"\nError during downconversion: {e}", fg="red")
                click.secho("Continuing without 16-bit upload.", fg="yellow")

    click.secho("\nDone uploading this release.", fg="green")
    seedbox_uploader.execute_upload()


def edit_metadata(
    path, tags, metadata, source, rls_data, recompress, source_url=None, is_apple_music=False
):  # auto_rename, spectral_ids, and skip_integrity_check removed
    """
    The metadata editing portion of the uploading process. Tags are automatically
    applied without prompting for review.
    """
    # Ensure rls_type is present before continuing
    if not metadata.get("rls_type"):
        click.secho("Warning: No release type found in metadata. Please select one:", fg="yellow")
        metadata["rls_type"] = _prompt_for_release_type()
    
    # For Apple Music, ensure album-level artists exist
    # The scraped metadata should already have artists at the album level
    # If not, we need to error out as this is required for upload
    if is_apple_music:
        if not metadata.get("artists") or not metadata["artists"]:
            click.secho("ERROR: No artist information available in scraped metadata for Apple Music upload!", fg="red", bold=True)
            click.secho("Please try a different URL or use manual metadata entry.", fg="yellow")
            raise click.Abort()
    
    # Check if scraped metadata has "Various Artists" as the main artist
    has_various_artists = False
    if metadata.get("artists"):
        main_artists_check = [a for a, i in metadata["artists"] if i == "main"]
        if len(main_artists_check) == 1 and main_artists_check[0].lower() == "various artists":
            has_various_artists = True
    
    # For all other sources (including Tidal), generate album-level artists from track metadata if missing
    # OR if scraped metadata has "Various Artists" - extract from file tags instead
    if not metadata.get("artists") or not metadata["artists"] or has_various_artists:
        # If Various Artists, extract from file tags to preserve per-track artist info
        if has_various_artists:
            # Extract artists from actual file tags
            all_artists = []
            for filename, tagset in tags.items():
                try:
                    # Get artist info from file tags
                    if hasattr(tagset, 'artist') and tagset.artist:
                        artist_list = tagset.artist if isinstance(tagset.artist, list) else [tagset.artist]
                        for artist in artist_list:
                            if artist and artist.strip():
                                # Add as main artist with importance "main"
                                all_artists.append((artist.strip(), "main"))
                except (TypeError, AttributeError):
                    pass
        else:
            # Extract all artists from track metadata (original behavior)
            all_artists = []
            for disc in metadata.get("tracks", {}).values():
                for track in disc.values():
                    if "artists" in track and track["artists"]:
                        all_artists.extend(track["artists"])
        
        # Deduplicate - keep both main and guest artists for now, prioritize main
        seen = set()
        main_artists = []
        guest_artists = []
        for artist, importance in all_artists:
            if artist.lower() not in seen:
                seen.add(artist.lower())
                if importance == "main":
                    main_artists.append((artist, importance))
                else:
                    guest_artists.append((artist, importance))
        
        # Use main artists if available, otherwise fall back to guest artists
        unique_artists = main_artists if main_artists else guest_artists
        metadata["artists"] = unique_artists
        
        if not unique_artists:
            click.secho("ERROR: No artist information found in track metadata!", fg="red", bold=True)
            click.secho("Track metadata structure:", fg="yellow")
            # Debug output - show first track to help diagnose
            if metadata.get("tracks"):
                first_disc = next(iter(metadata["tracks"].values()))
                if first_disc:
                    first_track = next(iter(first_disc.values()))
                    click.secho(f"Sample track keys: {list(first_track.keys())}", fg="yellow")
                    if "artists" in first_track:
                        click.secho(f"Sample track artists: {first_track['artists']}", fg="yellow")
            click.secho("Please try a different URL or use manual metadata entry.", fg="yellow")
            raise click.Abort()
    
    # Auto-tag files without prompting
    if not metadata["scene"]:
        tag_files(path, tags, metadata, False, source_url)  # auto_rename always False

    tags = check_tags(path)
    if not metadata["scene"] and recompress:
        recompress_path(path)
    check_folder_structure(path, metadata["scene"])

    # Convert genres to tags
    metadata["tags"] = convert_genres(metadata["genres"])

    # Refresh tags to accommodate differences in file structure
    tags = gather_tags(path)
    audio_info = gather_audio_info(path)
    return path, metadata, tags, audio_info


def _build_metadata_from_files(path, tags, rls_data):
    """
    Build metadata structure from file tags for Tidal URLs.
    Extracts all necessary information from the existing file metadata.
    """
    # Initialize metadata structure (matching EMPTY_METADATA from pre_data.py)
    metadata = {
        "format": rls_data["format"],
        "encoding": rls_data["encoding"],
        "encoding_vbr": rls_data["encoding_vbr"],
        "scene": rls_data["scene"],
        "source": rls_data["source"],
        "artists": [],
        "title": None,
        "rls_type": None,
        "year": None,
        "group_year": None,
        "date": None,
        "edition_title": None,
        "label": None,
        "catno": None,
        "tracks": {},
        "genres": [],
        "cover": None,
        "upc": None,
        "comment": None,
        "urls": [],
    }
    
    # Extract data from file tags
    # Group tracks by disc number
    tracks_by_disc = {}
    all_artists = []
    album_titles = []
    years = []
    labels = []
    catnos = []
    
    for filename, tagset in tags.items():
        try:
            # Extract disc number (default to 1)
            disc_num = 1
            if hasattr(tagset, 'discnumber') and tagset.discnumber:
                try:
                    disc_num = int(str(tagset.discnumber).split('/')[0])
                except (ValueError, AttributeError):
                    disc_num = 1
            
            # Extract track number
            track_num = 1
            if hasattr(tagset, 'tracknumber') and tagset.tracknumber:
                try:
                    track_num = int(str(tagset.tracknumber).split('/')[0])
                except (ValueError, AttributeError):
                    track_num = 1
            
            # Extract track title
            track_title = tagset.title if hasattr(tagset, 'title') and tagset.title else "Unknown"
            
            # Extract artist(s)
            track_artists = []
            if hasattr(tagset, 'artist') and tagset.artist:
                artist_list = tagset.artist if isinstance(tagset.artist, list) else [tagset.artist]
                for artist in artist_list:
                    if artist and artist.strip():
                        track_artists.append((artist.strip(), "main"))
                        all_artists.append((artist.strip(), "main"))
            
            # Extract album title
            if hasattr(tagset, 'album') and tagset.album:
                album_titles.append(tagset.album)
            
            # Extract year
            if hasattr(tagset, 'date') and tagset.date:
                try:
                    year = int(str(tagset.date)[:4])
                    years.append(year)
                except (ValueError, AttributeError):
                    pass
            
            # Extract label
            if hasattr(tagset, 'label') and tagset.label:
                labels.append(tagset.label)
            
            # Extract catalog number
            if hasattr(tagset, 'catalognumber') and tagset.catalognumber:
                catnos.append(tagset.catalognumber)
            
            # Build track metadata
            if disc_num not in tracks_by_disc:
                tracks_by_disc[disc_num] = {}
            
            tracks_by_disc[disc_num][track_num] = {
                "title": track_title,
                "artists": track_artists,
            }
            
        except (TypeError, AttributeError) as e:
            click.secho(f"Warning: Could not extract metadata from {filename}: {e}", fg="yellow")
            continue
    
    # Deduplicate and assign artists
    seen_artists = set()
    unique_artists = []
    for artist, importance in all_artists:
        if artist.lower() not in seen_artists:
            seen_artists.add(artist.lower())
            unique_artists.append((artist, importance))
    
    metadata["artists"] = unique_artists
    
    # Assign most common values
    if album_titles:
        metadata["title"] = max(set(album_titles), key=album_titles.count)
    
    if years:
        metadata["year"] = max(set(years), key=years.count)
        metadata["group_year"] = metadata["year"]  # Set group_year same as year
    
    if labels:
        metadata["label"] = max(set(labels), key=labels.count)
    
    if catnos:
        metadata["catno"] = max(set(catnos), key=catnos.count)
    
    # Assign tracks
    metadata["tracks"] = tracks_by_disc
    
    # Try to determine release type from track count
    total_tracks = sum(len(disc) for disc in tracks_by_disc.values())
    if total_tracks == 1:
        metadata["rls_type"] = "Single"
    elif total_tracks <= 4:
        metadata["rls_type"] = "EP"
    else:
        metadata["rls_type"] = "Album"
    
    # Validate we have required data
    if not metadata["artists"]:
        click.secho("ERROR: No artist information found in file tags!", fg="red", bold=True)
        raise click.Abort()
    
    if not metadata["title"]:
        click.secho("ERROR: No album title found in file tags!", fg="red", bold=True)
        raise click.Abort()
    
    click.secho(f"Extracted metadata from files:", fg="green")
    click.secho(f"  Artists: {', '.join(a[0] for a in metadata['artists'][:3])}", fg="green")
    click.secho(f"  Album: {metadata['title']}", fg="green")
    click.secho(f"  Type: {metadata['rls_type']}", fg="green")
    if metadata["year"]:
        click.secho(f"  Year: {metadata['year']}", fg="green")
    
    return metadata


def metadata_validator(metadata):
    """Validate that the provided metadata is not an issue."""
    metadata = metadata_validator_base(metadata)
    if metadata["format"] not in FORMATS.values():
        raise InvalidMetadataError(f"{metadata['format']} is not a valid format.")
    if metadata["encoding"] not in ENCODINGS:
        raise InvalidMetadataError(f"{metadata['encoding']} is not a valid encoding.")

    return metadata



def upload_and_report(
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
    source_url,
    seedbox_uploader,
    source=None,
    override_description=None,
    # override_lossy_comment=None,  # removed
):
    # Prepare upload parameters
    upload_kwargs = {
        "gazelle_site": gazelle_site,
        "path": path,
        "group_id": group_id,
        "metadata": metadata,
        "cover_url": cover_url,
        "track_data": track_data,
        "hybrid": hybrid,
        # "lossy_master": lossy_master,  # removed
        # "spectral_urls": spectral_urls,  # removed
        # "spectral_ids": spectral_ids,  # removed
        # "lossy_comment": lossy_comment,  # removed
        # "request_id": request_id,  # removed
        "source_url": source_url,
        **({"override_description": override_description} if override_description else {}),
    }

    # Execute upload
    torrent_id, group_id, torrent_path, torrent_content = prepare_and_upload(**upload_kwargs)

    # Lossy master reporting removed
    # if lossy_master:
    #     report_lossy_master(
    #         gazelle_site,
    #         torrent_id,
    #         spectral_urls,
    #         spectral_ids,
    #         source,
    #         override_lossy_comment if override_lossy_comment else lossy_comment,
    #         source_url=source_url,
    #     )

    # Generate URL
    url = f"{gazelle_site.base_url}/torrents.php?torrentid={torrent_id}"

    torrent_content.comment = url
    torrent_content.write(torrent_path, overwrite=True)

    # Display success message
    click.secho(
        f"Successfully uploaded {url} ({os.path.basename(path)}).",
        fg="green",
        bold=True,
    )

    # Copy URL to clipboard
    if cfg.upload.description.copy_uploaded_url_to_clipboard:
        pyperclip.copy(url)

    # Add to seedbox upload queue
    if cfg.upload.upload_to_seedbox:
        click.secho("Add uploading task.", fg="green")
        # Check if it's a FLAC file
        is_flac = metadata.get("format", "").upper() == "FLAC"
        seedbox_uploader.add_upload_task(path, task_type="folder", is_flac=is_flac)
        seedbox_uploader.add_upload_task(torrent_path, task_type="seed", is_flac=is_flac)

    return torrent_id, group_id, torrent_path, torrent_content, url


def convert_genres(genres):
    """Convert the weirdly spaced genres to RED-compliant genres."""
    return ",".join(re.sub("[-_ ]", ".", g).strip() for g in genres)


def _prompt_for_release_type():
    """Prompt user to select a release type if not found in metadata."""
    from brucelee94.constants import RELEASE_TYPES
    types_list = list(RELEASE_TYPES.values())
    click.echo("Available release types:")
    for i, rls_type in enumerate(types_list, 1):
        click.echo(f"  {i}. {rls_type}")
    
    while True:
        choice = click.prompt("Enter the number for the release type", type=int)
        if 1 <= choice <= len(types_list):
            return types_list[choice - 1]
        click.secho("Invalid choice. Please try again.", fg="red")


def _prompt_source():
    click.echo(f"\nValid sources: {', '.join(SOURCES.values())}")
    while True:
        sauce = click.prompt(
            click.style("What is the source of this release? [a]bort", fg="magenta"),
            default="",
        )
        try:
            return SOURCES[sauce.lower()]
        except KeyError:
            if sauce.lower().startswith("a"):
                raise click.Abort from None
            click.secho(f"{sauce} is not a valid source.", fg="red")
