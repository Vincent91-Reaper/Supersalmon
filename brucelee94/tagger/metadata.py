import asyncio
import json
from copy import copy
from itertools import islice

import click

from brucelee94 import cfg
from brucelee94.common import handle_scrape_errors, make_searchstrs, re_strip
from brucelee94.constants import RELEASE_TYPES
from brucelee94.search import SEARCHSOURCES, run_metasearch
from brucelee94.tagger.combine import combine_metadatas
from brucelee94.tagger.sources import METASOURCES
from brucelee94.tagger.sources.base import generate_artists


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


def _prompt_for_release_type():
    """Prompt user to select a release type if not found in metadata."""
    types_list = list(RELEASE_TYPES.keys())
    click.echo("Available release types:")
    for i, rls_type in enumerate(types_list, 1):
        click.echo(f"  {i}. {rls_type}")
    
    while True:
        choice = click.prompt("Enter the number for the release type", type=int)
        if 1 <= choice <= len(types_list):
            return types_list[choice - 1]
        click.secho(f"Invalid choice. Please enter a number between 1 and {len(types_list)}", fg="red")


def get_metadata(path, tags, rls_data=None, provided_source_url=None):
    """
    Get metadata from a URL provided by the user. Skips automatic search.
    If provided_source_url is given, use it directly instead of prompting.
    """
    # Initialize rls_data if needed
    rls_data = rls_data or {}
    if "urls" not in rls_data:
        rls_data["urls"] = []
    
    # If a source URL was provided (e.g., for 16-bit downconversion), use it directly
    if provided_source_url:
        url_input = provided_source_url
        click.secho(f"\nUsing provided source URL: {url_input}", fg="cyan")
    else:
        # Normal flow: prompt for URL
        import sys
        while True:
            # Only show prompt if stdin is a TTY (interactive mode)
            if sys.stdin.isatty():
                click.echo(
                    click.style(
                        "\nPlease provide a URL to scrape metadata from (or [m]anual, [a]bort): ",
                        fg="magenta",
                    ),
                    nl=False,
                )
                sys.stdout.flush()
                url_input = sys.stdin.readline().strip()
            else:
                # Non-TTY mode (piped input from bl94_helper): read silently
                url_input = sys.stdin.readline().strip()
            
            if url_input.lower().startswith("m"):
                metadata = _get_manual_metadata(rls_data)
                return metadata, None
            elif url_input.lower().startswith("a"):
                raise click.Abort()
            
            # Break out of prompt loop to scrape
            break
    
    # Try to scrape from the URL
    source_url = None
    metadata = None
    
    for name, source in METASOURCES.items():
        if source.Scraper.regex.match(url_input):
            click.secho(f"Scraping metadata from {name}...", fg="cyan")
            source_url = url_input
            if url_input not in rls_data["urls"]:
                rls_data["urls"].append(url_input)
            
            scraper = source.Scraper()
            # Create async task and run it
            loop = _get_event_loop()
            task = handle_scrape_errors(scraper.scrape_release(url_input))
            metadata = loop.run_until_complete(task)
            
            if metadata:
                # Clean and prepare metadata
                metadata = clean_metadata(metadata)
                remove_various_artists(metadata["tracks"])
                
                # Validate required fields
                if not metadata.get("rls_type"):
                    click.secho("Warning: No release type found in metadata. Please select one:", fg="yellow")
                    metadata["rls_type"] = _prompt_for_release_type()
                
                return metadata, source_url
            else:
                click.secho(f"Failed to scrape metadata from {url_input}", fg="red")
                if provided_source_url:
                    # If we were given a URL and it failed, raise an error
                    raise click.Abort("Failed to scrape from provided URL")
                break
    
    if not metadata:
        if provided_source_url:
            raise click.Abort("URL not recognized or failed to scrape")
        click.secho(f"URL not recognized or failed to scrape. Please try again.", fg="red")
        # Recursively try again
        return get_metadata(path, tags, rls_data, provided_source_url)


def _print_search_results(results, rls_data=None):
    """Print the results from the metadata source."""
    if rls_data:
        _print_metadata(rls_data, metadata_name="Previous")

    choices = {}
    choice_id = 1
    not_found = list(SEARCHSOURCES.keys())
    inactive_sources = []
    source_errors = SEARCHSOURCES.keys() - [r for r in results]

    for source, releases in results.items():
        if releases:
            click.secho(f"\nResults for {source}:", fg="yellow", bold=True)
            not_found.remove(source)
            results = dict(islice(releases.items(), cfg.upload.search.limit))
            for rls_id, release in results.items():
                choices[choice_id] = (source, rls_id)
                url = SEARCHSOURCES[source].Searcher.format_url(rls_id)
                click.secho(f"> {choice_id:02d} {release[1]} | {url}")
                choice_id += 1
        if releases is None:
            inactive_sources.append(source)
            not_found.remove(source)

    if not_found:
        click.echo()
        for source in not_found:
            click.echo(f"No results found from {source}.")

    if inactive_sources:
        for source in inactive_sources:
            click.echo(f"{source} is inactive. Update your config.py with the necessary tokens to enable it.")
    if source_errors:
        click.echo()
        click.secho(f"Failed to scrape {', '.join(source_errors)}.", fg="red")

    return choices


def _select_choice(choices, rls_data):
    source_url = None
    """
    Allow the user to select a metadata choice. Then, if the metadata came from a scraper,
    run the scrape(s) and return combined metadata.
    """
    # Initialize rls_data if needed
    rls_data = rls_data or {}
    if "urls" not in rls_data:
        rls_data["urls"] = []

    while True:
        if choices:
            res = click.prompt(
                click.style(
                    "\nWhich metadata results would you like to use? Other "
                    'options: paste URLs, [m]anual, [a], prefix choice or URL with "*" to indicate source (WEB)',
                    fg="magenta",
                ),
                type=click.STRING,
            )
        else:
            res = click.prompt(
                click.style(
                    "\nNo metadata results were found. Options: paste URLs, "
                    '[m]anual, [a]bort, prefix URL with "*" to indicate source (WEB)',
                    fg="magenta",
                ),
                type=click.STRING,
            )

        if res.lower().startswith("m"):
            return _get_manual_metadata(rls_data), None
        elif res.lower().startswith("a"):
            raise click.Abort

        sources, tasks = [], []
        for r in res.split():
            # Handle starred items first
            stripped = r[1:] if r.startswith("*") else r

            # Handle URLs (both starred and unstarred)
            if stripped.lower().startswith("http"):
                # Add any URL to rls_data urls if not already there
                if stripped not in rls_data["urls"]:
                    rls_data["urls"].append(stripped)

                # Set source_url if this is a starred URL
                if r.startswith("*"):
                    source_url = stripped

                # Try to scrape if it matches a metadata source
                for name, source in METASOURCES.items():
                    if source.Scraper.regex.match(stripped):
                        sources.append(name)
                        tasks.append(source.Scraper().scrape_release(stripped))
                        break
            # Handle numeric choices
            elif stripped.strip().isdigit() and int(stripped) in choices:
                scraper = METASOURCES[choices[int(stripped)][0]].Scraper()
                sources.append(choices[int(stripped)][0])
                tasks.append(handle_scrape_errors(scraper.scrape_release_from_id(choices[int(stripped)][1])))
                # Set source_url if this is a starred choice
                if r.startswith("*"):
                    source_url = SEARCHSOURCES[choices[int(stripped)][0]].Searcher.format_url(choices[int(stripped)][1])

        if not tasks:
            # Go to manual mode only if we have any URLs
            if rls_data["urls"]:
                meta = _get_manual_metadata(rls_data)
                meta["urls"] = meta.get("urls", [])
                # If we have a source_url (from a starred URL), make sure it's included
                if source_url and source_url not in meta["urls"]:
                    meta["urls"].append(source_url)
                return meta, source_url
            continue

        loop = _get_event_loop()
        metadatas = loop.run_until_complete(asyncio.gather(*tasks))
        meta = combine_metadatas(
            *((s, m) for s, m in zip(sources, metadatas, strict=False) if m), base=rls_data, source_url=source_url
        )
        meta = clean_metadata(meta)
        meta["artists"], meta["tracks"] = generate_artists(meta["tracks"])
        return meta, source_url


def _get_manual_metadata(rls_data):
    """
    Use the metadata built from the file tags as a base, then allow the user to edit
    that dictionary.
    """
    metadata = json.dumps(rls_data, indent=2, ensure_ascii=False)
    while True:
        try:
            metadata = click.edit(metadata, extension=".json", editor=cfg.upload.default_editor) or metadata
            metadata_dict = json.loads(metadata)
            if isinstance(metadata_dict["genres"], str):
                metadata_dict["genres"] = [metadata_dict["genres"]]
            return metadata_dict
        except (TypeError, json.decoder.JSONDecodeError):
            click.confirm(
                click.style("Metadata is not a valid JSON file, retry?", fg="magenta", bold=True),
                default=True,
                abort=True,
            )


def _print_metadata(metadata, metadata_name="Pending"):
    """Print the metadata that is a part of the new metadata."""
    click.secho(f"\n{metadata_name} metadata:", fg="yellow", bold=True)
    click.echo(f"> TRACK COUNT   : {sum(len(d.values()) for d in metadata['tracks'].values())}")
    click.echo("> ARTISTS:")
    for artist in metadata["artists"]:
        click.echo(f">>>  {artist[0]} [{artist[1]}]")
    click.echo(f"> TITLE         : {metadata['title']}")
    click.echo(f"> GROUP YEAR    : {metadata['group_year']}")
    click.echo(f"> YEAR          : {metadata['year']}")
    click.echo(f"> EDITION TITLE : {metadata['edition_title']}")
    click.echo(f"> LABEL         : {metadata['label']}")
    click.echo(f"> CATNO         : {metadata['catno']}")
    click.echo(f"> UPC           : {metadata['upc']}")
    click.echo(f"> GENRES        : {'; '.join(metadata['genres'])}")
    click.echo(f"> RELEASE TYPE  : {metadata['rls_type']}")
    click.echo(f"> COMMENT       : {metadata['comment']}")
    click.echo("> URLS:")
    for url in metadata["urls"]:
        click.echo(f">>> {url}")


def remove_various_artists(tracks):
    for _dnum, disc in tracks.items():
        for _tnum, track in disc.items():
            artists = []
            for artist, importance in track["artists"]:
                if "various artists" not in artist.lower() or artist.lower().strip() != "various":
                    artists.append((artist, importance))
            track["artists"] = artists


def clean_metadata(metadata):
    for disc, tracks in metadata["tracks"].items():
        for num, track in tracks.items():
            for artist, importance in copy(track["artists"]):
                guest_artists = {re_strip(a) for a, i in track["artists"] if i in {"guest", "remixer"}}
                if re_strip(artist) in guest_artists and importance == "main":
                    if sum("main" in item for item in metadata["tracks"][disc][num]["artists"]) == 1:
                        pass
                    else:
                        metadata["tracks"][disc][num]["artists"].remove((artist, importance))

    if metadata["catno"] and metadata["catno"].replace(" ", "") == str(metadata["upc"]):
        metadata["catno"] = None
    return metadata
