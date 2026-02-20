import os
import shutil

import click

from brucelee94 import cfg
from brucelee94.constants import ALLOWED_EXTENSIONS
from brucelee94.errors import NoncompliantFolderStructure


def has_long_file_paths(path, max_length=180):
    """
    Check if any file paths in the directory exceed the specified length.
    Returns True if any file path is longer than max_length characters.
    """
    root_len = len(cfg.directory.download_directory) + 1
    for root, _, files in os.walk(path):
        # Check if subfolder path exceeds limit
        if len(os.path.abspath(root)) - root_len > max_length:
            return True
        # Check each file path
        for f in files:
            filepath = os.path.abspath(os.path.join(root, f))
            filepathlen = len(filepath) - root_len
            if filepathlen > max_length:
                return True
    return False


def check_folder_structure(path, scene, genres=None, is_tidal=False, from_url=False):
    """
    Run through every filesystem check that causes uploads to violate the rules
    or be rejected on the upload form. Only verify that path lengths <180.
    
    Smart detection logic:
    - For Tidal URLs: Always check (no genre info available in files)
    - For other URL sources (Qobuz, Deezer, Apple Music, Beatport): 
      Check only if files have long paths (>180 chars)
    - For non-URL uploads: Check if classical genre OR if files have long paths
    """
    # For Tidal, always run the check (no genre info available)
    if is_tidal:
        pass  # Continue to run the check
    # For other URL sources, check only if files actually have long paths
    elif from_url:
        if not has_long_file_paths(path):
            # No long paths detected, skip the check
            return
    # For non-URL uploads, check if classical OR if files have long paths
    else:
        is_classical = genres and any('classical' in str(g).lower() for g in genres)
        has_long_paths = has_long_file_paths(path)
        
        if not is_classical and not has_long_paths:
            # Not classical and no long paths, skip the check
            return
    
    while True:
        click.secho("\nChecking folder structure...", fg="cyan", bold=True)
        try:
            _check_illegal_folders(path)
            _check_path_lengths(path, scene)
            return
        except NoncompliantFolderStructure:
            if scene:
                click.secho(
                    "The folder structure is not compliant with the upload rules. "
                    "As this is a scene release, you need to manually descene it before upload.",
                    fg="red",
                    bold=True,
                )
                raise click.Abort() from None
            click.confirm(
                click.style(
                    "You need to manually fix the issues present in the upload's folder? "
                    "Send a [Y] once you have done so, or a [N] to abort.",
                    fg="magenta",
                    bold=True,
                ),
                default=False,
                abort=True,
            )


def _check_illegal_folders(path):
    """Verify illegal folders."""
    for root, dirs, _files in os.walk(path, topdown=False):
        for dirname in dirs:
            if dirname == "@eaDir":
                target_dir = os.path.join(root, dirname)
                while True:
                    resp = click.prompt(
                        f"Dirname {target_dir} is illegal. [D]elete, [A]bort, or [C]ontinue?",
                        default="D",
                    ).lower()
                    if resp[0].lower() == "d":
                        shutil.rmtree(target_dir)
                        break
                    elif resp[0].lower() == "a":
                        raise click.Abort
                    elif resp[0].lower() == "c":
                        break


def _check_path_lengths(path, scene):
    """Verify that all path lengths are <=180 characters."""
    offending_files = []
    root_len = len(cfg.directory.download_directory) + 1
    for root, _, files in os.walk(path):
        if len(os.path.abspath(root)) - root_len > 180:
            click.secho("A subfolder has a path length >180 characters.", fg="red")
            raise NoncompliantFolderStructure
        for f in files:
            filepath = os.path.abspath(os.path.join(root, f))
            if len(filepath) - root_len > 180:
                offending_files.append(filepath)

    if scene and offending_files:
        click.secho("The following files exceed 180 characters in length.", fg="red", bold=True)
        for f in offending_files:
            click.echo(f" >> {f}")
        raise NoncompliantFolderStructure

    if not offending_files:
        return click.secho("No paths exceed 180 characters in length.", fg="green")

    click.secho("The following exceed 180 characters in length, truncating...", fg="red")
    for filepath in sorted(offending_files):
        # Calculate how much we need to truncate
        # Target: relative path length <= 178 (leaving 2 chars for "..")
        target_relative_len = 178
        current_relative_len = len(filepath) - root_len
        excess = current_relative_len - target_relative_len
        
        # Get directory and filename components
        dir_part = os.path.dirname(filepath)
        file_basename = os.path.basename(filepath)
        filename_no_ext, ext = os.path.splitext(file_basename)
        
        # Safety check: ensure filename is long enough to truncate
        if len(filename_no_ext) < excess + 2:
            click.secho(
                f"Cannot truncate (filename too short): {filepath}",
                fg="red"
            )
            continue
        
        # Truncate the filename (not including extension) and add ".."
        truncated_filename = filename_no_ext[:len(filename_no_ext) - excess - 2]
        new_filename = truncated_filename + ".." + ext
        newpath = os.path.join(dir_part, new_filename)
        
        os.rename(filepath, newpath)
        click.echo(f" >> {newpath}")


def _check_zero_len_folder(path):
    """Verify that a zero length folder does not exist."""
    for root, _, files in os.walk(path):
        for filename in files:
            foldlist = os.path.join(root, filename)
            if "//" in foldlist:
                click.secho("A zero length folder exists in this directory.", fg="red")
                raise NoncompliantFolderStructure
    click.secho("No zero length folders were found.", fg="green")


def _check_extensions(path, scene):
    """Validate that all file extensions are valid."""
    mp3, aac, flac = [], [], []
    offending_files = []  # Collect offending files for scene releases
    for root, _, files in os.walk(path):
        for fln in files:
            _, ext = os.path.splitext(fln.lower())
            if ext == ".mp3":
                mp3.append(fln)
            elif ext == ".flac":
                flac.append(fln)
            elif ext == ".m4a":
                aac.append(fln)
            elif ext not in ALLOWED_EXTENSIONS:
                if scene:
                    offending_files.append(os.path.join(root, fln))
                else:
                    _handle_bad_extension(os.path.join(root, fln), scene)

    if scene and offending_files:
        click.secho("The following files have invalid extensions:", fg="red", bold=True)
        for filepath in offending_files:
            click.echo(f" >> {filepath}")
        raise NoncompliantFolderStructure

    if len([li for li in [mp3, flac, aac] if li]) > 1:
        _handle_multiple_audio_exts()
    else:
        click.secho("File extensions have been validated.", fg="green")


def _handle_bad_extension(filepath, scene):
    while True:
        resp = click.prompt(
            f"{filepath} does not have an approved file extension. [D]elete, [a]bort, or [c]ontinue?",
            default="D",
        ).lower()
        if resp[0].lower() == "d":
            return os.remove(filepath)
        elif resp[0].lower() == "a":
            raise click.Abort
        elif resp[0].lower() == "c":
            return


def _handle_multiple_audio_exts():
    while True:
        resp = click.prompt(
            "There are multiple audio codecs in this folder. [A]bort or [c]ontinue?",
            default="A",
        ).lower()
        if resp[0] == "a":
            raise click.Abort
        if resp[0] == "c":
            return
