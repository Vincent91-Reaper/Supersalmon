import asyncio

import click

from brucelee94.errors import ScrapeError
from brucelee94.tagger.sources import (
    beatport,
    deezer,
    itunes,
    qobuz,
)

METASOURCES = {
    "iTunes": itunes,
    "Deezer": deezer,
    "Beatport": beatport,
    "Qobuz": qobuz,
}

loop = asyncio.get_event_loop()


async def run_metadata(url, sources=None, return_source_name=False):
    """Run a scrape for the metadata of a URL"""
    sources = METASOURCES if not sources else {name: source for name, source in METASOURCES.items() if name in sources}
    for name, source in sources.items():
        if source.Scraper.regex.match(url):
            click.secho(f"Getting metadata from {name}.", fg="cyan")
            if return_source_name:
                return await source.Scraper().scrape_release(url), name
            return await source.Scraper().scrape_release(url)
    raise ScrapeError("URL did not match a scraper.")
