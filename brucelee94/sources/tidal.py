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
        params = params or {}
        album_id = self.parse_release_id(url)
        
        for cc in get_tidal_regions_to_fetch():
            try:
                self.country_code = cc
                params["countrycode"] = cc
                
                data = await self.get_json(f"/albums/{album_id}", params=params)
                
                # Add limit parameter to ensure we get tracks
                tracks_params = params.copy()
                tracks_params["limit"] = 100  # Request up to 100 tracks
                
                tracklist_url = f"/albums/{album_id}/tracks"
                tracklist = await self.get_json(tracklist_url, params=tracks_params)
                
                if not tracklist.get("items"):
                    # Continue to try next region instead of failing here
                    if cc != get_tidal_regions_to_fetch()[-1]:
                        continue
                
                data["tracklist"] = tracklist["items"]
                return data
            except json.decoder.JSONDecodeError as e:
                raise ScrapeError("Tidal page did not return valid JSON.") from e
            except (KeyError, ScrapeError) as e:
                pass
        raise ScrapeError(f"Failed to grab metadata for {url}.")


def get_tidal_regions_to_fetch():
    # TODO: maybe make this a validation
    if cfg.metadata.tidal.fetch_regions:
        return cfg.metadata.tidal.fetch_regions
    else:
        raise ScrapeError("No regions defined for Tidal to grab from")
