import asyncio
import os
import platform
import re
import shutil

import click
import mutagen.flac
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
from brucelee94.tagger.cover import download_cover_if_nonexistent
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
    generate_catno,
    generate_description,
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
            
            # Special case: Tidal/Deezer URLs - extract metadata from file tags instead of scraping
            if metadata.get("_extract_from_files"):
                click.secho("Extracting metadata from file tags...", fg="cyan")
                source_url = metadata.get("_source_url")
                is_tidal = metadata.get("_is_tidal", False)
                is_deezer = metadata.get("_is_deezer", False)
                
                # Build metadata from file tags (pass is_deezer for BARCODE handling)
                # Also get updated path in case folder was renamed (e.g., Various Artists detection)
                metadata, path = _build_metadata_from_files(path, tags, rls_data, is_deezer=is_deezer)
                
                # Skip retagging for Tidal/Deezer - files are already correct
                # Skip the edit_metadata workflow entirely
                # Just check tags and folder structure
                tags = check_tags(path)
                if recompress:
                    recompress_path(path)
                # Run folder structure check
                # For Tidal: Always check (files don't have genre tags, so is_tidal=True)
                # For Deezer: Use genre info (files have genre tags, so is_tidal=False)
                check_folder_structure(path, metadata["scene"], metadata.get("genres", []), is_tidal=is_tidal, from_url=True)
                
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
                
                # For Apple Music: If UPC wasn't scraped, try to extract it from file tags
                if is_apple_music and not metadata.get("upc"):
                    upcs = []
                    for filename, tagset in tags.items():
                        try:
                            # Try 'upc' field first, then 'barcode' field
                            if hasattr(tagset, 'upc') and tagset.upc:
                                upcs.append(str(tagset.upc))
                            elif hasattr(tagset, 'barcode') and tagset.barcode:
                                upcs.append(str(tagset.barcode))
                        except (TypeError, AttributeError):
                            continue
                    
                    # Use most common UPC if found
                    if upcs:
                        metadata["upc"] = max(set(upcs), key=upcs.count)

        if not group_id:
            # Dupe recheck removed - directly proceed
            click.echo()
        track_data = concat_track_data(tags, audio_info)
        
        # SIMPLE UNIFIED LABEL HANDLING (replaces all special cases)
        # For Qobuz/Apple Music: Check if album artist == label with keywords
        if not _extract_from_files:  # Qobuz/Apple Music workflow
            try:
                # Get current album artist from tags
                current_albumartist = None
                for filename, tagset in tags.items():
                    if hasattr(tagset, 'albumartist') and tagset.albumartist:
                        current_albumartist = tagset.albumartist
                        break
                
                if current_albumartist:
                    # Extract label from metadata
                    extracted_label = metadata.get("_original_label") or metadata.get("label")
                    
                    # Simple check: album artist == label AND label has keywords
                    if extracted_label and current_albumartist.lower().strip() == extracted_label.lower().strip():
                        if _has_label_keywords(extracted_label):
                            click.secho(f"\nDetected label '{extracted_label}' as album artist (has keywords)", fg="cyan")
                            click.secho("Processing as Various Artists compilation...", fg="cyan")
                            
                            # Process: Retag to Various Artists, clean tracks, rename folder
                            path = _process_label_as_various_artists(
                                path, tags, extracted_label, metadata
                            )
                            
                            # Refresh tags after processing
                            tags = gather_tags(path)
                            click.secho("Label handling complete.\n", fg="green")
            
            except Exception as e:
                click.secho(f"Error in label handling: {e}", fg="yellow", err=True)
                import traceback
                traceback.print_exc()
        
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

    # Handle cover image - prepare cover but don't upload to ptpimg yet
    cover_to_upload_later = None
    is_cover_downloaded = False
    if is_16bit_transcode:
        # For 16-bit transcodes, skip uploading cover to ptpimg entirely
        # The cover.jpg was already copied to the folder during downconversion
        # RED will use the local cover.jpg file from the torrent
        cover_path = os.path.join(path, "cover.jpg")
        if os.path.exists(cover_path):
            click.secho("Skipping cover upload to ptpimg for 16-bit transcode (using local cover.jpg)", fg="cyan")
        else:
            click.secho("Warning: cover.jpg not found in 16-bit folder", fg="yellow")
    elif group_id:
        if not remove_downloaded_cover_image:
            download_cover_if_nonexistent(path, metadata["cover"])
        # Don't need cover URL for existing groups
        pass
    else:
        # For new groups, prepare cover but upload to ptpimg AFTER torrent upload
        cover_path, is_cover_downloaded = download_cover_if_nonexistent(path, metadata["cover"])
        cover_to_upload_later = cover_path



    # Request filling removed
    # if not request_id and cfg.upload.requests.check_requests:
    #     request_id = check_requests(gazelle_site, searchstrs)

    # Upload torrent WITHOUT cover URL first (faster, helps be first to upload)
    torrent_id, group_id, torrent_path, torrent_content, url, newgroup = upload_and_report(
        gazelle_site,
        path,
        group_id,
        metadata,
        None,  # Upload without cover_url first
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

    # Fetch group info to determine if this is truly a new group
    # by checking the number of torrents in the group
    loop = asyncio.get_event_loop()
    group_data = loop.run_until_complete(gazelle_site.torrentgroup(group_id))
    torrent_count = len(group_data.get("torrents", []))
    is_new_group = (torrent_count == 1)  # New group if only 1 torrent (the one we just uploaded)
    
    # Let print_torrents fetch and preprocess the data itself by passing rset=None
    print_torrents(gazelle_site, group_id, rset=None, highlight_torrent_id=torrent_id)

    # Update the specific torrent with label and catalog (post-upload)
    label_to_add = metadata.get("label", "")
    catalog_to_add = generate_catno(metadata)
    
    if label_to_add or catalog_to_add:
        click.secho("Adding label and catalog to torrent...", fg="cyan")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            gazelle_site.update_torrent_metadata(
                torrent_id,
                label=label_to_add,
                catalog_number=catalog_to_add
            )
        )
        click.secho("Label and catalog added successfully!", fg="green")

    # Update group with cover and description after torrent is uploaded (new groups only)
    album_desc_to_add = None
    cover_url_to_add = None
    
    # Handle cover upload if needed (new groups only)
    if cover_to_upload_later and not is_16bit_transcode and is_new_group:
        click.secho("Uploading cover image to ptpimg...", fg="cyan")
        cover_url_to_add = upload_cover(cover_to_upload_later)
        # Generate album description to include with cover update (new groups only)
        album_desc_to_add = generate_description(track_data, metadata)
    elif is_cover_downloaded and remove_downloaded_cover_image:
        click.secho("Removing downloaded Cover Image File", fg="yellow")
        os.remove(cover_to_upload_later)
    
    # Update group with cover and description (new groups only)
    if cover_url_to_add or album_desc_to_add:
        click.secho("Adding cover and description to torrent group...", fg="cyan")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            gazelle_site.update_group_cover_image(
                group_id,
                cover_url=cover_url_to_add,
                album_desc=album_desc_to_add
            )
        )
        click.secho("Cover and description added successfully!", fg="green")

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
    
    # SPECIAL CASE 4 DETECTION FOR APPLE MUSIC: Check for record label as album artist
    # This handles Various Artists compilations where label appears everywhere
    if is_apple_music:
        # Get current album artist from tags
        current_albumartist = None
        for filename, tagset in tags.items():
            if hasattr(tagset, 'albumartist') and tagset.albumartist:
                current_albumartist = tagset.albumartist
                break
        
        if current_albumartist:
            # Extract label from metadata
            extracted_label = metadata.get("label")
            
            # Collect all unique track artists
            track_artists_for_detection = set()
            for filename, tagset in tags.items():
                if hasattr(tagset, 'artist') and tagset.artist:
                    artist_list = tagset.artist if isinstance(tagset.artist, list) else [tagset.artist]
                    for artist in artist_list:
                        if artist and artist.strip():
                            individual_artists = [a.strip() for a in str(artist).split(',') if a.strip()]
                            for individual_artist in individual_artists:
                                track_artists_for_detection.add(individual_artist)
            
            # Check if this is a record label album (Special Case 4)
            if extracted_label and len(track_artists_for_detection) >= 3:
                is_label_album = _is_record_label_album(
                    current_albumartist, 
                    extracted_label, 
                    list(track_artists_for_detection)
                )
                
                if is_label_album:
                    click.echo()
                    click.secho(f"Detected record label as album artist: {current_albumartist}", fg="yellow")
                    click.secho("This appears to be a various artists compilation.", fg="yellow")
                    click.secho("Retagging album artist to 'Various Artists'...", fg="cyan")
                    
                    # Retag all files' albumartist to "Various Artists"
                    _retag_albumartist_to_various_artists(tags)
                    
                    # Clean track artist tags to remove the label (Special Case 4)
                    click.secho("Removing label from track artist tags...", fg="cyan")
                    label_to_remove = current_albumartist
                    
                    for filename, tagset in tags.items():
                        try:
                            # Handle FLAC files
                            if hasattr(tagset, 'artist') and tagset.artist:
                                artist_list = tagset.artist if isinstance(tagset.artist, list) else [tagset.artist]
                                cleaned_list = []
                                
                                for artist_str in artist_list:
                                    if artist_str and artist_str.strip():
                                        artist_str = str(artist_str).strip()
                                        
                                        # Try to clean using helper function
                                        cleaned = _clean_artist_string_with_label(artist_str, label_to_remove)
                                        
                                        if cleaned:
                                            # Check if the original string contained any separator
                                            separators = [';', ',', '/', '\\', '&', '+', '|']
                                            found_sep = None
                                            for sep in separators:
                                                if sep in artist_str:
                                                    found_sep = sep
                                                    break
                                            
                                            if found_sep:
                                                # Split the cleaned result by the detected separator
                                                cleaned_list.extend([p.strip() for p in cleaned.split(found_sep) if p.strip()])
                                            else:
                                                cleaned_list.append(cleaned)
                                        else:
                                            # Keep the original artist if it's already clean (no label to remove)
                                            cleaned_list.append(artist_str)
                                
                                # Update artist field with cleaned list
                                if cleaned_list:
                                    tagset.artist = cleaned_list if len(cleaned_list) > 1 else cleaned_list[0]
                                    click.secho(f"  Cleaned track artist in {os.path.basename(filename)}", fg="white")
                            
                            # Handle MP3 files (TPE1 field)
                            if hasattr(tagset, 'mut') and hasattr(tagset.mut, 'tags'):
                                if 'TPE1' in tagset.mut.tags:
                                    tpe1_val = tagset.mut.tags['TPE1']
                                    if hasattr(tpe1_val, 'text') and tpe1_val.text:
                                        artist_list = tpe1_val.text if isinstance(tpe1_val.text, list) else [tpe1_val.text]
                                        cleaned_list = []
                                        
                                        for artist_str in artist_list:
                                            if artist_str and str(artist_str).strip():
                                                artist_str = str(artist_str).strip()
                                                
                                                # Try to clean using helper function
                                                cleaned = _clean_artist_string_with_label(artist_str, label_to_remove)
                                                
                                                if cleaned:
                                                    # Check if the original string contained any separator
                                                    separators = [';', ',', '/', '\\', '&', '+', '|']
                                                    found_sep = None
                                                    for sep in separators:
                                                        if sep in artist_str:
                                                            found_sep = sep
                                                            break
                                                    
                                                    if found_sep:
                                                        # Split the cleaned result by the detected separator
                                                        cleaned_list.extend([p.strip() for p in cleaned.split(found_sep) if p.strip()])
                                                    else:
                                                        cleaned_list.append(cleaned)
                                        
                                        # Update TPE1 field with cleaned list
                                        if cleaned_list:
                                            from mutagen.id3 import TPE1
                                            tagset.mut.tags['TPE1'] = TPE1(encoding=3, text=cleaned_list)
                                            click.secho(f"  Cleaned track artist in {os.path.basename(filename)}", fg="white")
                            
                            # Save the changes to the file
                            tagset.save()
                            
                        except Exception as e:
                            click.secho(f"Warning: Could not clean track artist in {filename}: {e}", fg="yellow")
                    
                    click.secho("Track artist tags cleaned successfully.", fg="green")
                    
                    # Rename folder from "Record Label - ..." to "Various Artists - ..."
                    path = _rename_folder_with_various_artists(path)
                    
                    # Update metadata to reflect Various Artists
                    # Collect all track artists and treat as main artists
                    all_track_artists = []
                    for artist_name in track_artists_for_detection:
                        if artist_name.lower() != label_to_remove.lower():
                            all_track_artists.append((artist_name, "main"))
                    metadata["artists"] = all_track_artists
                    
                    # Update label to use original label
                    if extracted_label and metadata.get("label") != extracted_label:
                        metadata["label"] = extracted_label
                        click.secho(f"Label updated for upload: {extracted_label}", fg="cyan")
                    
                    # Refresh tags to reflect changes
                    tags = gather_tags(path)
                    
                    click.secho("Album will be treated as Various Artists compilation.", fg="green")
                    click.echo()
    
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
        
        # Apply Various Artists replacement logic
        # This will replace "Various Artists" with track artists if it's the only album artist
        metadata["artists"] = replace_various_artists_with_track_artists(metadata["artists"], metadata)
        
        if not metadata["artists"]:
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
    
    # Check if this is a DJ Mix release and adjust artist roles accordingly
    # DJ Mix pattern: matches "DJ Mix", "DJMix", "DJ-Mix" etc. (case-insensitive)
    if metadata.get("rls_type") == "DJ Mix" and metadata.get("artists"):
        # For DJ Mix releases, the album artist should be the DJ/Compiler
        # and track artists should be the main artists
        # Extract album artist from file tags (albumartist field)
        album_artists = []
        for filename, tagset in tags.items():
            if hasattr(tagset, 'albumartist') and tagset.albumartist:
                aa_list = tagset.albumartist if isinstance(tagset.albumartist, list) else [tagset.albumartist]
                for aa in aa_list:
                    if aa and aa.strip():
                        album_artists.append(aa.strip())
        
        # Deduplicate album artists
        album_artists = list(set(album_artists))
        
        # If we found album artists, restructure the artist list
        if album_artists:
            new_artists = []
            
            # Add album artists as DJ/Compiler (importance 6)
            for aa in album_artists:
                new_artists.append((aa, "djcompiler"))
            
            # Get track artists from individual file tags (not scraped metadata)
            track_artists_set = set()
            album_artists_lower = [aa.lower() for aa in album_artists]
            
            # Extract artists from individual track files
            for filename, tagset in tags.items():
                if hasattr(tagset, 'artist') and tagset.artist:
                    # Handle both string and list formats
                    artists_list = tagset.artist if isinstance(tagset.artist, list) else [tagset.artist]
                    for artist in artists_list:
                        artist_clean = artist.strip()
                        # Split on both ", " and " & " to separate multiple artists
                        # e.g., "Alix Perez, Shades & Eprom" -> ["Alix Perez", "Shades", "Eprom"]
                        sub_artists = []
                        for comma_part in artist_clean.split(', '):
                            sub_artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
                        
                        for sub_artist in sub_artists:
                            if sub_artist and sub_artist.lower() not in album_artists_lower:
                                if sub_artist not in track_artists_set:
                                    track_artists_set.add(sub_artist)
            
            # Add track artists as main (importance 1)
            for artist in sorted(track_artists_set):
                new_artists.append((artist, "main"))
            
            # Update metadata with new artist list
            metadata["artists"] = new_artists
            
            click.secho(f"Detected DJ Mix release. DJ/Compiler: {', '.join(album_artists)}", fg="cyan")
            
            # Remove "(DJ Mix)" suffix from title for cleaner group name
            # Keep detection in title, but remove suffix for display
            original_title = metadata["title"]
            metadata["title"] = re.sub(r'\s*\(DJ[\s\-]*Mix\)\s*$', '', metadata["title"], flags=re.IGNORECASE).strip()
        else:
            click.secho("WARNING: DJ Mix detected but no albumartist tag found in files", fg="red")
    
    # Auto-tag files without prompting
    if not metadata["scene"]:
        tag_files(path, tags, metadata, False, source_url)  # auto_rename always False

    tags = check_tags(path)
    if not metadata["scene"] and recompress:
        recompress_path(path)
    # Always run folder structure check when metadata was scraped from a URL
    # (Qobuz, Tidal, Deezer, Apple Music, Beatport)
    check_folder_structure(path, metadata["scene"], metadata.get("genres", []), from_url=bool(source_url))

    # Convert genres to tags
    metadata["tags"] = convert_genres(metadata["genres"])

    # Refresh tags to accommodate differences in file structure
    tags = gather_tags(path)
    audio_info = gather_audio_info(path)
    return path, metadata, tags, audio_info


def replace_various_artists_with_track_artists(artists, metadata):
    """
    Replace "Various Artists" with actual track artists when it's the only album artist.
    
    This handles special cases where files from Tidal/Deezer (or scraped from Qobuz/Apple Music)
    have "Various Artists" as the album artist, which causes upload failures.
    
    Args:
        artists: List of (artist_name, importance) tuples
        metadata: Metadata dict containing tracks information
    
    Returns:
        List of (artist_name, importance) tuples with "Various Artists" replaced if needed
    """
    # Check if "Various Artists" is the only album artist
    if len(artists) == 1 and artists[0][0].lower() == "various artists":
        # Extract all unique track artists (main importance only)
        track_artists = set()
        
        if "tracks" in metadata and metadata["tracks"]:
            for disc_tracks in metadata["tracks"].values():
                for track_info in disc_tracks.values():
                    if "artists" in track_info:
                        for artist_name, importance in track_info["artists"]:
                            if importance == "main":
                                track_artists.add(artist_name)
        
        # Replace "Various Artists" with track artists if we found any
        if track_artists:
            result = [(artist, "main") for artist in sorted(track_artists)]
            return result
        else:
            return artists
    
    # Keep original artists if:
    # - Not "Various Artists"
    # - "Various Artists" plus other artists (intentional)
    # - No track artists found (fallback)
    return artists


def _has_label_keywords(label):
    """
    Check if label contains label keywords that indicate it's a record label.
    Prevents false positives for self-released albums where artist name == label.
    
    Keywords: Records, Production, Music, Entertainment, Label, Recordings,
              Productions, Media, Group, Collective, Imprint
    
    Args:
        label: The record label string to check
    
    Returns:
        bool: True if label contains any of the keywords, False otherwise
    """
    if not label:
        return False
    
    label_lower = label.lower()
    keywords = [
        'records', 'production', 'music', 'entertainment', 'label',
        'recordings', 'productions', 'media', 'group', 'collective', 'imprint'
    ]
    
    return any(keyword in label_lower for keyword in keywords)


def _remove_label_from_track_artists(tags, label):
    """
    Remove label from all track artist tags in both FLAC and MP3 files.
    Uses _clean_artist_string_with_label() helper for cleaning.
    
    Args:
        tags: Dictionary of filename -> tagset mappings
        label: The label string to remove from track artists
    """
    if not label:
        return
    
    click.secho(f"Removing '{label}' from track artist tags...", fg="cyan")
    
    for filename, tagset in tags.items():
        # Handle FLAC files
        if hasattr(tagset, 'artist') and tagset.artist:
            artist_list = tagset.artist if isinstance(tagset.artist, list) else [tagset.artist]
            cleaned_list = []
            
            for artist_str in artist_list:
                if artist_str and artist_str.strip():
                    artist_str = str(artist_str).strip()
                    cleaned = _clean_artist_string_with_label(artist_str, label)
                    
                    if cleaned:
                        cleaned_list.append(cleaned)
                    else:
                        # Keep original if no label found
                        cleaned_list.append(artist_str)
            
            if cleaned_list:
                tagset.artist = cleaned_list
                tagset.save()
        
        # Handle MP3 files (TPE1)
        if hasattr(tagset, 'mut') and 'TPE1' in tagset.mut.tags:
            tpe1_value = tagset.mut.tags['TPE1'].text
            artist_list = tpe1_value if isinstance(tpe1_value, list) else [tpe1_value]
            cleaned_list = []
            
            for artist_str in artist_list:
                if artist_str and artist_str.strip():
                    artist_str = str(artist_str).strip()
                    cleaned = _clean_artist_string_with_label(artist_str, label)
                    
                    if cleaned:
                        cleaned_list.append(cleaned)
                    else:
                        # Keep original if no label found
                        cleaned_list.append(artist_str)
            
            if cleaned_list:
                from mutagen.id3 import TPE1
                tagset.mut.tags['TPE1'] = TPE1(encoding=3, text=cleaned_list)
                tagset.mut.save()
    
    click.secho("Track artist tags cleaned successfully.", fg="green")


def _process_label_as_various_artists(path, tags, label, metadata):
    """
    Unified processing when label is detected as album artist.
    
    Simple approach:
    1. Retag album artist to "Various Artists"
    2. Remove label from track artist tags
    3. Rename folder
    4. Update metadata
    
    Args:
        path: Current folder path
        tags: Dictionary of filename -> tagset mappings
        label: The record label detected as album artist
        metadata: Metadata dictionary to update
    
    Returns:
        Updated path (if folder was renamed) or original path
    """
    if not label:
        return path
    
    click.secho(f"\nDetected record label as album artist: {label}", fg="yellow")
    click.secho("This appears to be a various artists compilation.", fg="yellow")
    
    # Step 1: Retag album artist to "Various Artists"
    click.secho("Retagging album artist to 'Various Artists'...", fg="cyan")
    _retag_albumartist_to_various_artists(tags)
    
    # Step 2: Remove label from track artist tags
    _remove_label_from_track_artists(tags, label)
    
    # Step 3: Rename folder
    click.secho("\nRenaming folder...", fg="cyan")
    new_path = _rename_folder_with_various_artists(path)
    if new_path != path:
        click.secho(f"Renamed folder:", fg="green")
        click.secho(f"  From: {os.path.basename(path)}", fg="white")
        click.secho(f"  To:   {os.path.basename(new_path)}", fg="white")
        path = new_path
    
    # Step 4: Update metadata label
    if metadata and metadata.get("label") != label:
        metadata["label"] = label
        click.secho(f"Label updated for upload: {label}", fg="green")
    
    click.secho("\nAlbum will be treated as Various Artists compilation.", fg="green")
    
    return path


def _clean_artist_string_with_label(artist_str, label_to_remove):
    """
    Helper function to clean an artist string by removing the label.
    Handles multiple separators: semicolon (;), comma (,), forward slash (/), 
    backslash (\), ampersand (&), plus (+), and pipe (|).
    
    Args:
        artist_str: Artist string that may contain label (e.g., "War Child Records; Arctic Monkeys")
        label_to_remove: Label name to remove
    
    Returns:
        Cleaned artist string with label removed, or None if no changes needed
    """
    if not artist_str or not label_to_remove:
        return None
    
    artist_str = str(artist_str).strip()
    label_lower = label_to_remove.lower()
    
    # Common separators used in artist tags (in priority order)
    # Semicolon and comma first as they're most common
    separators = [';', ',', '/', '\\', '&', '+', '|']
    
    # Try each separator
    for sep in separators:
        if sep in artist_str:
            parts = [p.strip() for p in artist_str.split(sep) if p.strip()]
            original_count = len(parts)
            # Filter out the label (case-insensitive)
            parts = [p for p in parts if p.lower() != label_lower]
            
            # Only return if we actually removed something
            if parts and len(parts) < original_count:
                # Preserve the separator style in output
                if len(parts) > 1:
                    # Use the same separator with proper spacing
                    if sep in [';', ',']:
                        return f'{sep} '.join(parts)
                    else:
                        return f' {sep} '.join(parts)
                else:
                    return parts[0]
    
    # Fallback: Check if label is a substring and remove it
    if label_lower in artist_str.lower():
        # Try case-insensitive replacement
        import re
        pattern = re.compile(re.escape(label_to_remove), re.IGNORECASE)
        cleaned = pattern.sub('', artist_str).strip()
        # Clean up any leftover separators
        cleaned = re.sub(r'^[;,/\\&+|]\s*', '', cleaned)
        cleaned = re.sub(r'\s*[;,/\\&+|]$', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        if cleaned and cleaned != artist_str:
            return cleaned
    
    return None


def _detect_label_in_folder_only(path, albumartist, track_artists_list):
    """
    Detect if folder name contains a label but the album artist tag is clean (SPECIAL CASE 3).
    
    This handles Qobuz downloads where:
    - Album artist tag is clean (e.g., "Swoze")
    - Folder name contains label (e.g., "Swoze, Former City Records - Album")
    - Track artist tags contain the label
    
    Detection criteria:
    1. Folder name contains comma-separated parts with label keywords
    2. Album artist is clean (doesn't contain that label part)
    3. The label part appears in track artists list
    
    Args:
        path: Path to the album folder
        albumartist: The album artist from tags (should be clean)
        track_artists_list: List of unique track artist names
    
    Returns:
        The label name to remove, or None if this case doesn't apply
    """
    if not albumartist or not track_artists_list or not path:
        return None
    
    # Get folder name without path
    folder_name = os.path.basename(path)
    
    # Check if folder name contains comma-separated parts before " - "
    if ',' not in folder_name or ' - ' not in folder_name:
        return None
    
    # Extract artist part from folder name (before " - ")
    folder_artist_part = folder_name.split(' - ')[0]
    
    # Split into parts
    folder_parts = [part.strip() for part in folder_artist_part.split(',') if part.strip()]
    
    # Need at least 2 parts
    if len(folder_parts) < 2:
        return None
    
    # Keywords that indicate a record label
    label_keywords = [
        "records", "music", "entertainment", "label", "recordings",
        "productions", "media", "group", "collective", "imprint"
    ]
    
    # Find label parts in folder name that are NOT in album artist
    for part in folder_parts:
        part_lower = part.lower()
        
        # Check if this part has label keywords
        has_keyword = any(keyword in part_lower for keyword in label_keywords)
        
        if has_keyword:
            # Check if album artist is clean (doesn't contain this label)
            if part.lower().strip() not in albumartist.lower():
                # Check if this label appears in track artists
                for track_artist in track_artists_list:
                    if part.lower().strip() == track_artist.lower().strip():
                        # Found it! Label in folder/track artists but NOT in album artist
                        return part
    
    return None


def _detect_label_in_albumartist(albumartist, label, track_artists_list):
    """
    Detect if album artist contains both artist name and label name (e.g., "Swoze, Former City Records").
    
    This is for the special case where the album artist tag contains BOTH the real artist 
    and the record label, separated by commas. We want to remove the label and keep only 
    the real artist name.
    
    Detection criteria:
    1. Album artist contains multiple comma-separated parts
    2. One part contains label keywords (Records, Music, etc.)
    3. The label part also appears in track artists list (confirming it's incorrectly tagged)
    
    Args:
        albumartist: The album artist name from file tags (e.g., "Swoze, Former City Records")
        label: The record label extracted from metadata (not used in this new logic)
        track_artists_list: List of unique track artist names
    
    Returns:
        The label name to remove, or None if this case doesn't apply
    """
    if not albumartist or not track_artists_list:
        return None
    
    # Check if album artist contains comma-separated parts
    if ',' not in albumartist:
        return None
    
    # Split album artist into parts
    artist_parts = [part.strip() for part in albumartist.split(',') if part.strip()]
    
    # Need at least 2 parts
    if len(artist_parts) < 2:
        return None
    
    # Keywords that indicate a record label
    label_keywords = [
        "records", "music", "entertainment", "label", "recordings",
        "productions", "media", "group", "collective", "imprint"
    ]
    
    # Find which parts contain label keywords
    for part in artist_parts:
        part_lower = part.lower()
        # Check if this part has label keywords
        has_keyword = any(keyword in part_lower for keyword in label_keywords)
        
        if has_keyword:
            # Check if this label part appears in track artists
            # This confirms it's incorrectly tagged as a track artist too
            for track_artist in track_artists_list:
                if part.lower().strip() == track_artist.lower().strip():
                    # Found it! This label is incorrectly in both album artist and track artists
                    return part
    
    return None


def _is_record_label_album(albumartist, label, track_artists_list):
    """
    Detect if the album artist is a record label (not a real artist) for a various artists album.
    
    Detection logic: Compare album artist to record label, check for multiple track artists,
    verify no track artist matches album artist, and check for label keywords.
    If all criteria are met, the album artist is the label and should be changed to "Various Artists".
    
    Criteria for detection:
    1. Album artist matches (or is very similar to) the record label
    2. Album has multiple different track artists (3+)
    3. None of the track artists closely match the album artist name
    4. Album artist name contains keywords that imply it's a record label
       (e.g., "Records", "Music", "Productions", etc.)
    
    Args:
        albumartist: The album artist name from file tags
        label: The record label extracted from file metadata
        track_artists_list: List of unique track artist names
    
    Returns:
        Boolean indicating if this appears to be a record label album
    """
    if not albumartist or not label or not track_artists_list:
        return False
    
    albumartist_lower = albumartist.lower().strip()
    label_lower = label.lower().strip()
    
    # Skip if already Various Artists
    if albumartist_lower == "various artists":
        return False
    
    # Condition 1: Check if album artist matches or is very similar to the label
    match_found = False
    
    # Exact match
    if albumartist_lower == label_lower:
        match_found = True
    # Check if one contains the other (e.g., "Ed Banger Records" contains "Ed Banger")
    elif albumartist_lower in label_lower or label_lower in albumartist_lower:
        # Require substantial overlap (at least 60% of shorter string)
        shorter = min(len(albumartist_lower), len(label_lower))
        overlap = len(albumartist_lower) if albumartist_lower in label_lower else len(label_lower)
        if overlap / shorter >= 0.6:
            match_found = True
    
    if not match_found:
        return False
    
    # Condition 2: Check if album has multiple different track artists (at least 3 for various artists)
    if len(track_artists_list) < 3:
        return False
    
    # Condition 3: Check if MOST track artists are different from the album artist name
    # (If most tracks have different artists, it's likely a Various Artists compilation)
    # Allow the label to appear in some tracks (e.g., label sampler, intro/outro tracks)
    matching_artists = 0
    for track_artist in track_artists_list:
        track_artist_lower = track_artist.lower().strip()
        # Check for exact or partial match
        if track_artist_lower == albumartist_lower:
            matching_artists += 1
        elif albumartist_lower in track_artist_lower or track_artist_lower in albumartist_lower:
            matching_artists += 1
    
    # If more than 50% of track artists match the album artist, it's likely a solo artist album
    # If less than 50% match, it's likely a Various Artists compilation with the label as album artist
    if matching_artists >= len(track_artists_list) * 0.5:
        return False
    
    # Condition 4: Check if album artist name contains label keywords
    # This helps distinguish actual labels from self-released albums where artist = label
    label_keywords = [
        "records", "music", "entertainment", "label", "recordings",
        "productions", "media", "group", "collective", "imprint"
    ]
    
    contains_keyword = False
    for keyword in label_keywords:
        if keyword in albumartist_lower:
            contains_keyword = True
            break
    
    if not contains_keyword:
        return False
    
    # All 4 criteria met: likely a record label album
    return True


def _retag_albumartist_to_various_artists(tags):
    """
    Retag all files' albumartist field to "Various Artists".
    
    Args:
        tags: Dictionary of file tags
    """
    for filename, tagset in tags.items():
        try:
            # Set albumartist to "Various Artists"
            tagset.albumartist = "Various Artists"
            # Save the changes to the file
            tagset.save()
        except Exception as e:
            click.secho(f"Warning: Could not retag {filename}: {e}", fg="yellow")


def _rename_folder_with_various_artists(path):
    """
    Rename folder from "Record Label - Album..." to "Various Artists - Album..."
    
    Args:
        path: Current folder path
    
    Returns:
        New folder path after renaming
    """
    import os
    import re
    
    basename = os.path.basename(path)
    parent_dir = os.path.dirname(path)
    
    # Pattern to extract artist from folder name
    # Format: "Artist - Album (Year) [Source Format] [Bit-Sample]"
    # We want to replace everything before " - " with "Various Artists"
    pattern = r"^(.+?)\s+-\s+(.+)$"
    match = re.match(pattern, basename)
    
    if match:
        # Replace artist with "Various Artists"
        new_basename = f"Various Artists - {match.group(2)}"
        new_path = os.path.join(parent_dir, new_basename)
        
        # Rename the folder
        try:
            os.rename(path, new_path)
            click.secho(f"\nRenamed folder:", fg="cyan")
            click.secho(f"  From: {basename}", fg="white")
            click.secho(f"  To:   {new_basename}", fg="green")
            return new_path
        except Exception as e:
            click.secho(f"Warning: Could not rename folder: {e}", fg="yellow")
            return path
    
    return path


def _build_metadata_from_files(path, tags, rls_data, is_deezer=False):
    """
    Build metadata structure from file tags for Tidal and Deezer URLs.
    Extracts all necessary information from the existing file metadata.
    
    Also detects and handles record label albums (where label is tagged as album artist).
    
    Args:
        path: Path to the album folder
        tags: Dictionary of file tags
        rls_data: Release data dictionary
        is_deezer: Boolean indicating if this is a Deezer upload (for BARCODE handling)
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
        "tags": None,
    }
    
    # Extract data from file tags
    # Group tracks by disc number
    tracks_by_disc = {}
    all_artists = []
    album_titles = []
    years = []
    dates = []
    labels = []
    catnos = []
    genres = []
    upcs = []
    
    # First pass: Extract album artists to distinguish main artists from guest artists
    # Album artists are artists who appear at the album level (albumartist field)
    # Track artists who also appear as album artists are "main" artists
    # Track artists who don't appear as album artists are "guest" artists
    # 
    # IMPORTANT: Exclude "Various Artists" from the set because it's a placeholder, not a real artist
    # When album artist is only "Various Artists", all track artists should be treated as "main"
    album_artists_set = set()
    original_albumartist = None  # Store the original album artist for record label detection
    for filename, tagset in tags.items():
        if hasattr(tagset, 'albumartist') and tagset.albumartist:
            aa_list = tagset.albumartist if isinstance(tagset.albumartist, list) else [tagset.albumartist]
            for aa in aa_list:
                if aa and aa.strip():
                    # Store the first album artist we find for record label detection
                    if original_albumartist is None:
                        original_albumartist = str(aa).strip()
                    
                    # Split by comma to handle cases like "Ismail Candide, Eddy Woogy"
                    individual_artists = [a.strip() for a in str(aa).split(',') if a.strip()]
                    for individual_artist in individual_artists:
                        # Skip "Various Artists" - it's a placeholder, not a real artist
                        if individual_artist.lower() != "various artists":
                            # Store in lowercase for case-insensitive comparison
                            album_artists_set.add(individual_artist.lower())
    
    # Pre-scan: Collect all unique track artists for record label detection
    track_artists_for_detection = set()
    for filename, tagset in tags.items():
        if hasattr(tagset, 'artist') and tagset.artist:
            artist_list = tagset.artist if isinstance(tagset.artist, list) else [tagset.artist]
            for artist in artist_list:
                if artist and artist.strip():
                    individual_artists = [a.strip() for a in str(artist).split(',') if a.strip()]
                    for individual_artist in individual_artists:
                        track_artists_for_detection.add(individual_artist)
    
    # Pre-scan: Extract label for record label detection
    # We need to extract the label before checking if album artist is a label
    extracted_label = None
    for filename, tagset in tags.items():
        # Try to get copyright field from the underlying mutagen object
        copyright_text = None
        try:
            if hasattr(tagset, 'mut'):
                # For FLAC files, the tags are in a dictionary-like object
                if isinstance(tagset.mut, mutagen.flac.FLAC):
                    # Try different case variations
                    for key in ['copyright', 'COPYRIGHT', 'Copyright']:
                        if key in tagset.mut:
                            copyright_val = tagset.mut.get(key)
                            if copyright_val:
                                copyright_text = copyright_val[0] if isinstance(copyright_val, list) else copyright_val
                                break
        except (AttributeError, KeyError, IndexError, TypeError):
            pass
        
        if copyright_text:
            copyright_text = str(copyright_text).strip()
            
            # Clean up copyright text by removing common distribution phrases
            copyright_text = re.sub(r'\s*under exclusive license to\s*', ' ', copyright_text, flags=re.IGNORECASE)
            copyright_text = re.sub(r',?\s*a division of [^,]+', '', copyright_text, flags=re.IGNORECASE)
            copyright_text = re.sub(r'\s+', ' ', copyright_text).strip()
            
            # Parse copyright: first try to extract label after year
            match = re.search(r'\d{4}\s+(.+)', copyright_text)
            if match:
                extracted_label = match.group(1).strip()
            else:
                # If no year pattern, use the entire copyright text as label
                extracted_label = copyright_text
            
            # If we found a label, we can stop looking
            if extracted_label:
                break
        
        # Try label field if copyright didn't work
        if not extracted_label and hasattr(tagset, 'label') and tagset.label:
            extracted_label = str(tagset.label).strip()
            if extracted_label:
                break
    
    # SIMPLE UNIFIED LABEL HANDLING for Tidal/Deezer
    # Check if album artist == label with keywords
    if original_albumartist and extracted_label:
        if original_albumartist.lower().strip() == extracted_label.lower().strip():
            if _has_label_keywords(extracted_label):
                click.secho(f"\nDetected label '{extracted_label}' as album artist (has keywords)", fg="cyan")
                click.secho("Processing as Various Artists compilation...", fg="cyan")
                
                # Process: Retag to Various Artists, clean tracks, rename folder
                path = _process_label_as_various_artists(
                    path, tags, extracted_label, metadata
                )
                
                # Clear album_artists_set since we're treating this as Various Artists
                album_artists_set = set()
                
                click.secho("Label handling complete.\n", fg="green")
    
    
    # Second pass: Extract track data and classify artists
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
                        # Split by comma to handle cases like "Gayga, Din" -> ["Gayga", "Din"]
                        individual_artists = [a.strip() for a in str(artist).split(',') if a.strip()]
                        for individual_artist in individual_artists:
                            # Determine if this artist is a main artist or guest artist
                            # Main artist: appears at both album level (albumartist) and track level
                            # Guest artist: appears only at track level (not in albumartist)
                            # 
                            # SPECIAL CASE: If album_artists_set is empty (e.g., album artist was "Various Artists"),
                            # treat all track artists as "main" by default
                            if not album_artists_set:
                                # No real album artists found (only "Various Artists" or empty)
                                # All track artists are main artists
                                importance = "main"
                            elif individual_artist.lower() in album_artists_set:
                                importance = "main"
                            else:
                                importance = "guest"
                            
                            track_artists.append((individual_artist, importance))
                            all_artists.append((individual_artist, importance))
            
            # Extract album title
            if hasattr(tagset, 'album') and tagset.album:
                album_titles.append(tagset.album)
            
            # Extract year and full date
            # Try recordingdate first (this is the actual release date), then fall back to date field
            date_to_use = None
            
            # Try recordingdate from underlying mutagen object first
            try:
                if hasattr(tagset, 'mut'):
                    # For FLAC files, the tags are in a dictionary-like object
                    if isinstance(tagset.mut, mutagen.flac.FLAC):
                        # Try different case variations
                        for key in ['recordingdate', 'RECORDINGDATE', 'Recordingdate']:
                            if key in tagset.mut:
                                date_val = tagset.mut.get(key)
                                if date_val:
                                    date_to_use = date_val[0] if isinstance(date_val, list) else date_val
                                    break
            except (AttributeError, KeyError, IndexError, TypeError):
                pass
            
            # Fall back to date field if recordingdate not found
            if not date_to_use and hasattr(tagset, 'date') and tagset.date:
                date_to_use = str(tagset.date)
            
            if date_to_use and date_to_use != 'None':
                try:
                    year = int(str(date_to_use)[:4])
                    years.append(year)
                    # Keep full date string for date field
                    dates.append(str(date_to_use))
                except (ValueError, AttributeError):
                    pass
            
            # Extract label from copyright field first, then try label field
            label_extracted = False
            
            # Try to get copyright field from the underlying mutagen object
            copyright_text = None
            try:
                if hasattr(tagset, 'mut'):
                    # For FLAC files, the tags are in a dictionary-like object
                    if isinstance(tagset.mut, mutagen.flac.FLAC):
                        # Try different case variations
                        for key in ['copyright', 'COPYRIGHT', 'Copyright']:
                            if key in tagset.mut:
                                copyright_val = tagset.mut.get(key)
                                if copyright_val:
                                    copyright_text = copyright_val[0] if isinstance(copyright_val, list) else copyright_val
                                    break
            except (AttributeError, KeyError, IndexError, TypeError) as e:
                pass
            
            if copyright_text:
                copyright_text = str(copyright_text).strip()
                
                # Clean up copyright text by removing common distribution phrases
                # Example: "(P) 2025 Slaughter Gang, LLC under exclusive license to Epic Records, a division of Sony Music Entertainment"
                # -> "Slaughter Gang, LLC Epic Records"
                copyright_text = re.sub(r'\s*under exclusive license to\s*', ' ', copyright_text, flags=re.IGNORECASE)
                copyright_text = re.sub(r',?\s*a division of [^,]+', '', copyright_text, flags=re.IGNORECASE)
                copyright_text = re.sub(r'\s+', ' ', copyright_text).strip()  # Normalize whitespace
                
                label_from_copyright = None
                
                # Parse copyright: first try to extract label after year
                # Example: "1997 HOMmega Productions" -> "HOMmega Productions"
                match = re.search(r'\d{4}\s+(.+)', copyright_text)
                if match:
                    label_from_copyright = match.group(1).strip()
                else:
                    # If no year pattern, use the entire copyright text as label
                    # Example: "Lemon Demon" -> "Lemon Demon"
                    label_from_copyright = copyright_text
                
                if label_from_copyright:
                    # Check for "Records DK" pattern (with or without numbers)
                    # Examples: "Records DK", "232131 Records DK", "3324569 Records DK"
                    if re.search(r'(?:\d+\s+)?Records\s+DK$', label_from_copyright, re.IGNORECASE):
                        labels.append("Self-Released")
                        label_extracted = True
                    else:
                        # Check if copyright/label matches any main artist name
                        # If it does, use "Self-Released" instead
                        main_artist_names = [artist[0] for artist in all_artists if artist[1] == "main"]
                        if label_from_copyright in main_artist_names:
                            labels.append("Self-Released")
                        else:
                            labels.append(label_from_copyright)
                        label_extracted = True
            
            # Try label field if copyright didn't work
            if not label_extracted:
                if hasattr(tagset, 'label'):
                    if tagset.label:
                        labels.append(str(tagset.label).strip())
            
            # Extract catalog number
            if hasattr(tagset, 'catalognumber') and tagset.catalognumber:
                catnos.append(tagset.catalognumber)
            
            # Extract UPC/Barcode (try both 'upc' and 'barcode' fields)
            barcode_value = None
            
            try:
                # Try UPC field first
                if hasattr(tagset, 'upc') and tagset.upc:
                    barcode_value = str(tagset.upc)
                # Try barcode field with hasattr
                elif hasattr(tagset, 'barcode') and tagset.barcode:
                    barcode_value = str(tagset.barcode)
                # For FLAC/Vorbis tags, try accessing via dictionary with various case variations
                else:
                    # Try to access tags as a dictionary (works for FLAC Vorbis comments)
                    tag_dict = None
                    
                    # TagFile wraps mutagen objects - access the underlying mutagen object
                    if hasattr(tagset, 'mut'):
                        mut_obj = tagset.mut
                        # For FLAC files, tags is the Vorbis comment dict
                        if hasattr(mut_obj, 'tags') and mut_obj.tags:
                            tag_dict = mut_obj.tags
                        # For direct mutagen objects (fallback)
                        elif hasattr(mut_obj, '__getitem__'):
                            tag_dict = mut_obj
                    elif hasattr(tagset, 'tags'):
                        tag_dict = tagset.tags
                    elif hasattr(tagset, '__dict__'):
                        # Some tag formats expose tags as attributes
                        tag_dict = tagset.__dict__
                    
                    if tag_dict:
                        # Try various case variations of barcode
                        for barcode_key in ['BARCODE', 'barcode', 'Barcode', 'CATALOGUENUMBER', 'CatalogueNumber']:
                            if barcode_key in tag_dict:
                                value = tag_dict[barcode_key]
                                # Handle list values (common in Vorbis comments)
                                if isinstance(value, list) and len(value) > 0:
                                    barcode_value = str(value[0])
                                elif value:
                                    barcode_value = str(value)
                                if barcode_value:
                                    break
                
                # If we found a barcode value, add it to appropriate lists
                if barcode_value:
                    upcs.append(barcode_value)
                    # For Deezer files, BARCODE = UPC = Catalogue number
                    # Add to catnos so it's used as the catalogue number
                    if is_deezer:
                        catnos.append(barcode_value)
            except Exception as e:
                # If BARCODE extraction fails, silently continue
                pass
            
            # Extract genre
            if hasattr(tagset, 'genre') and tagset.genre:
                genre_list = tagset.genre if isinstance(tagset.genre, list) else [tagset.genre]
                for genre in genre_list:
                    if genre and genre.strip():
                        genres.append(genre.strip())
            
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
    # Prioritize "main" importance over "guest" for the same artist
    seen_artists = {}  # dict to track artist name (lowercase) -> (original_name, importance)
    for artist, importance in all_artists:
        artist_lower = artist.lower()
        if artist_lower not in seen_artists:
            # First time seeing this artist
            seen_artists[artist_lower] = (artist, importance)
        else:
            # Artist already seen - prioritize "main" over "guest"
            existing_name, existing_importance = seen_artists[artist_lower]
            if existing_importance == "guest" and importance == "main":
                # Upgrade guest to main
                seen_artists[artist_lower] = (artist, importance)
            # If existing is "main" and new is "guest", keep existing (main)
            # If both are same importance, keep existing
    
    # Convert dict values to list
    unique_artists = list(seen_artists.values())
    
    metadata["artists"] = unique_artists
    
    # Replace "Various Artists" with track artists if it's the only album artist
    metadata["artists"] = replace_various_artists_with_track_artists(metadata["artists"], metadata)
    
    # Assign most common values
    if album_titles:
        raw_album_title = max(set(album_titles), key=album_titles.count)
        # Use parse_title from pre_data.py to extract edition from album title
        from brucelee94.tagger.pre_data import parse_title
        metadata["title"], metadata["edition_title"] = parse_title(raw_album_title)
    
    if years:
        metadata["year"] = max(set(years), key=years.count)
        metadata["group_year"] = metadata["year"]  # Set group_year same as year
    
    # Ensure year is set (required for remaster_year field)
    # If year is not set, try to extract from date or use a fallback
    if not metadata["year"]:
        # Try to extract year from date if available
        if dates:
            most_common_date = max(set(dates), key=dates.count)
            date_str = str(most_common_date).strip()
            # Extract year from date string (first 4 digits)
            year_match = re.search(r'(\d{4})', date_str)
            if year_match:
                metadata["year"] = int(year_match.group(1))
                metadata["group_year"] = metadata["year"]
        
        # If still no year, use current year as fallback (should rarely happen)
        if not metadata["year"]:
            from datetime import datetime
            current_year = datetime.now().year
            logger.warning(f"No year found in metadata, using current year: {current_year}")
            metadata["year"] = current_year
            metadata["group_year"] = current_year
    
    # Parse and format date for torrent description (Month Day, Year)
    if dates:
        most_common_date = max(set(dates), key=dates.count)
        try:
            # Parse various date formats and convert to "Month Day, Year"
            from datetime import datetime
            
            date_str = str(most_common_date).strip()
            
            # Check if date string is just a year (4 digits) with no other characters
            # If so, skip formatting to avoid defaulting to January 1
            if re.match(r'^\d{4}$', date_str):
                # Don't set the date field - we only have a year
                pass
            else:
                # Try common date formats (only for dates with month/day info)
                # Handle dates like "2025-10-02", "2025/10/02", "20251002"
                date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']
                parsed_date = None
                
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except (ValueError, TypeError):
                        continue
                
                if parsed_date:
                    # Format as "Month Day, Year" (e.g., "December 5, 2025")
                    try:
                        metadata["date"] = parsed_date.strftime("%B %-d, %Y") if platform.system() != "Windows" else parsed_date.strftime("%B %#d, %Y")
                    except (ValueError, TypeError):
                        # Fallback for platforms that don't support %- or %#
                        metadata["date"] = parsed_date.strftime("%B %d, %Y").replace(' 0', ' ')
        except Exception as e:
            click.secho(f"Warning: Could not parse date: {e}", fg="yellow")
    
    if labels:
        metadata["label"] = max(set(labels), key=labels.count)
    
    if catnos:
        metadata["catno"] = max(set(catnos), key=catnos.count)
    
    if upcs:
        metadata["upc"] = max(set(upcs), key=upcs.count)
    
    # Deduplicate genres
    if genres:
        metadata["genres"] = list(set(genres))
    else:
        metadata["genres"] = []
    
    # Convert genres to tags for RED compliance (always set, even if empty)
    metadata["tags"] = convert_genres(metadata["genres"])
    
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
    
    # Check if title contains "DJ Mix" and adjust release type and artist roles
    # DJ Mix pattern: matches "DJ Mix", "DJMix", "DJ-Mix" etc. (case-insensitive)
    if metadata.get("title") and re.search(r"DJ[\s\-]*Mix", metadata["title"], re.IGNORECASE):
        metadata["rls_type"] = "DJ Mix"
        
        # For DJ Mix releases, the album artist should be the DJ/Compiler
        # and track artists should be the main artists
        # Extract album artist from file tags (albumartist field)
        album_artists = []
        for filename, tagset in tags.items():
            if hasattr(tagset, 'albumartist') and tagset.albumartist:
                aa_list = tagset.albumartist if isinstance(tagset.albumartist, list) else [tagset.albumartist]
                for aa in aa_list:
                    if aa and aa.strip():
                        album_artists.append(aa.strip())
        
        # Deduplicate album artists
        album_artists = list(set(album_artists))
        
        # If we found album artists, restructure the artist list
        if album_artists:
            new_artists = []
            
            # Add album artists as DJ/Compiler (importance 6)
            for aa in album_artists:
                new_artists.append((aa, "djcompiler"))
            
            # Add track artists as main (importance 1), excluding album artists to avoid duplication
            album_artists_lower = [aa.lower() for aa in album_artists]
            seen_track_artists = set()
            for artist, importance in metadata["artists"]:
                if artist.lower() not in album_artists_lower:
                    # Split on both ", " and " & " to separate multiple artists
                    # e.g., "Alix Perez, Shades & Eprom" -> ["Alix Perez", "Shades", "Eprom"]
                    sub_artists = []
                    for comma_part in artist.split(', '):
                        sub_artists.extend([a.strip() for a in comma_part.split(' & ') if a.strip()])
                    
                    for sub_artist in sub_artists:
                        if sub_artist and sub_artist.lower() not in seen_track_artists:
                            new_artists.append((sub_artist, "main"))
                            seen_track_artists.add(sub_artist.lower())
            
            # Update metadata with new artist list
            metadata["artists"] = new_artists
            
            click.secho(f"Detected DJ Mix release. DJ/Compiler: {', '.join(album_artists)}", fg="cyan")
            
            # Remove "(DJ Mix)" suffix from title for cleaner group name
            original_title = metadata["title"]
            metadata["title"] = re.sub(r'\s*\(DJ[\s\-]*Mix\)\s*$', '', metadata["title"], flags=re.IGNORECASE).strip()
    
    # Validate we have required data
    if not metadata["artists"]:
        click.secho("ERROR: No artist information found in file tags!", fg="red", bold=True)
        raise click.Abort()
    
    if not metadata["title"]:
        click.secho("ERROR: No album title found in file tags!", fg="red", bold=True)
        raise click.Abort()
    
    # Return both metadata and path (path may have been updated if folder was renamed)
    return metadata, path


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
    torrent_id, group_id, torrent_path, torrent_content, newgroup = prepare_and_upload(**upload_kwargs)

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
        # Check if it's a FLAC file
        is_flac = metadata.get("format", "").upper() == "FLAC"
        seedbox_uploader.add_upload_task(path, task_type="folder", is_flac=is_flac)
        seedbox_uploader.add_upload_task(torrent_path, task_type="seed", is_flac=is_flac)

    return torrent_id, group_id, torrent_path, torrent_content, url, newgroup


def convert_genres(genres):
    """Convert the weirdly spaced genres to RED-compliant genres.
    Returns 'electronic' as fallback if no genres are present."""
    if not genres:
        return "electronic"
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
