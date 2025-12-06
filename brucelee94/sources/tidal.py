import json
import re

from brucelee94 import cfg
from brucelee94.errors import ScrapeError
from brucelee94.sources.base import BaseScraper


class TidalBase(BaseScraper):
    url = "https://api.tidalhifi.com/v1"
    site_url = "https://listen.tidal.com"
    image_url = "https://resources.tidal.com/images/{album_id}/1280x1280.jpg"
    regex = re.compile(r"^https*:\/\/.*?(?:tidal|wimpmusic)\.com.*?\/(album|track|playlist)\/([0-9a-z\-]+)")
    release_format = "/album/{rls_id}"
    get_params = {"token": cfg.metadata.tidal.token}

    def __init__(self):
        self.country_code = None
        super().__init__()

    @classmethod
    def format_url(cls, rls_id, rls_name=None):
        return cls.site_url + cls.release_format.format(rls_id=rls_id[1])

    @classmethod
    def parse_release_id(cls, url):
        return cls.regex.search(url)[2]

    async def create_soup(self, url, params=None):
        """Run a GET request to Tidal's JSON API for album data."""
        import click
        params = params or {}
        album_id = self.parse_release_id(url)
        click.secho(f"\nDEBUG TIDAL API: Fetching album {album_id}", fg="yellow")
        click.secho(f"DEBUG TIDAL API: Original URL: {url}", fg="yellow")
        
        for cc in get_tidal_regions_to_fetch():
            try:
                self.country_code = cc
                params["countrycode"] = cc
                click.secho(f"DEBUG TIDAL API: Trying region {cc}", fg="yellow")
                
                data = await self.get_json(f"/albums/{album_id}", params=params)
                click.secho(f"DEBUG TIDAL API: Album data keys: {list(data.keys())}", fg="yellow")
                click.secho(f"DEBUG TIDAL API: Album title: {data.get('title', 'N/A')}", fg="yellow")
                click.secho(f"DEBUG TIDAL API: numberOfTracks: {data.get('numberOfTracks', 'N/A')}", fg="yellow")
                
                # Add limit parameter to ensure we get tracks
                tracks_params = params.copy()
                tracks_params["limit"] = 100  # Request up to 100 tracks
                
                tracklist_url = f"/albums/{album_id}/tracks"
                click.secho(f"DEBUG TIDAL API: Fetching tracklist from: {tracklist_url} with limit=100", fg="yellow")
                tracklist = await self.get_json(tracklist_url, params=tracks_params)
                click.secho(f"DEBUG TIDAL API: Tracklist response keys: {list(tracklist.keys())}", fg="yellow")
                click.secho(f"DEBUG TIDAL API: Tracklist has {len(tracklist.get('items', []))} tracks", fg="yellow")
                
                if tracklist.get("items"):
                    first_track = tracklist["items"][0]
                    click.secho(f"DEBUG TIDAL API: First track keys: {list(first_track.keys())}", fg="yellow")
                    click.secho(f"DEBUG TIDAL API: First track artists: {first_track.get('artists', 'NOT PRESENT')}", fg="yellow")
                else:
                    click.secho(f"DEBUG TIDAL API: WARNING - No tracks in tracklist response!", fg="red")
                    click.secho(f"DEBUG TIDAL API: Full tracklist response: {tracklist}", fg="red")
                
                data["tracklist"] = tracklist["items"]
                return data
            except json.decoder.JSONDecodeError as e:
                click.secho(f"DEBUG TIDAL API: JSON decode error for region {cc}", fg="red")
                raise ScrapeError("Tidal page did not return valid JSON.") from e
            except (KeyError, ScrapeError) as e:
                click.secho(f"DEBUG TIDAL API: Error for region {cc}: {e}", fg="red")
                pass
        raise ScrapeError(f"Failed to grab metadata for {url}.")


def get_tidal_regions_to_fetch():
    # TODO: maybe make this a validation
    if cfg.metadata.tidal.fetch_regions:
        return cfg.metadata.tidal.fetch_regions
    else:
        raise ScrapeError("No regions defined for Tidal to grab from")
