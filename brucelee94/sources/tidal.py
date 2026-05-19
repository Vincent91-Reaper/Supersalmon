import json
import re
import time

import requests

from brucelee94 import cfg
from brucelee94.errors import ScrapeError
from brucelee94.sources.base import BaseScraper

TOKEN_CACHE_DURATION_SECONDS = 86400  # Cache extracted Tidal web token for 24 hours.


class TidalBase(BaseScraper):
    url = "https://tidal.com/v1"
    site_url = "https://listen.tidal.com"
    image_url = "https://resources.tidal.com/images/{album_id}/1280x1280.jpg"
    regex = re.compile(r"^https*:\/\/.*?(?:tidal|wimpmusic)\.com.*?\/(album|track|playlist)\/([0-9a-z\-]+)")
    release_format = "/album/{rls_id}"
    get_params = {}
    _web_token = None
    _web_token_fetched_at = 0

    def __init__(self):
        self.country_code = None
        super().__init__()

    @classmethod
    def format_url(cls, rls_id, rls_name=None):
        return cls.site_url + cls.release_format.format(rls_id=rls_id[1])

    @classmethod
    def parse_release_id(cls, url):
        return cls.regex.search(url)[2]

    @staticmethod
    def normalize_artists(artists):
        if isinstance(artists, dict):
            artists = [artists]
        elif isinstance(artists, str):
            artists = [{"name": artists, "type": "MAIN"}]
        elif not isinstance(artists, list):
            artists = []

        normalized = []
        for artist in artists:
            if isinstance(artist, str):
                normalized.append({"name": artist, "type": "MAIN"})
            elif isinstance(artist, dict) and artist.get("name"):
                normalized.append(artist)
        return normalized

    def _track_artists(self, track):
        if not isinstance(track, dict):
            return []
        return self.normalize_artists(track.get("artists") or track.get("artist"))

    def _tracklist_has_artists(self, tracklist):
        return any(self._track_artists(track) for track in tracklist)

    def _normalize_track_artists(self, track, album_artists):
        if not isinstance(track, dict):
            return track
        track["artists"] = self._track_artists(track) or album_artists
        return track

    @staticmethod
    def _unwrap_album_items(items):
        tracklist = []
        for item in items:
            track = item.get("item", item) if isinstance(item, dict) else item
            if isinstance(track, dict):
                tracklist.append(track)
        return tracklist

    async def _fetch_album_items(self, album_id, base_params):
        results = []
        offset = 0
        while True:
            track_resp = await self.get_json(
                f"/albums/{album_id}/items",
                params={**base_params, "limit": 100, "offset": offset},
                headers=self._headers(),
            )
            items = track_resp.get("items", [])
            results.extend(items)
            if len(items) < 100:
                break
            offset += 100
        return self._unwrap_album_items(results)

    async def _fetch_album_tracks(self, album_id, base_params):
        results = []
        offset = 0
        while True:
            track_resp = await self.get_json(
                f"/albums/{album_id}/tracks",
                params={**base_params, "limit": 100, "offset": offset},
                headers=self._headers(),
            )
            items = track_resp.get("items", [])
            results.extend(items)
            if len(items) < 100:
                break
            offset += 100
        return [item for item in results if isinstance(item, dict)]

    def _headers(self):
        token = cfg.metadata.tidal.token or self.get_web_token()
        return {"x-tidal-token": token} if token else {}

    @classmethod
    def get_web_token(cls):
        if cls._web_token and time.time() - cls._web_token_fetched_at < TOKEN_CACHE_DURATION_SECONDS:
            return cls._web_token
        try:
            html = requests.get("https://tidal.com", timeout=10).text
            asset = re.search(r'href="([^"]*assets/store[^"]+)"', html)
            if not asset:
                raise ScrapeError("Could not locate Tidal web asset for token extraction.")
            script_url = asset[1]
            if script_url.startswith("/"):
                script_url = f"https://tidal.com{script_url}"
            script = requests.get(script_url, timeout=10).text
            # Tidal bundles environment-specific token variable names near STAGE/PROD markers.
            stage_match = re.search(r"STAGE.*?\[([^,]+).*?PROD", script)
            if stage_match:
                token_match = re.search(rf"{re.escape(stage_match[1])}=.(\w+)", script)
            else:
                token_match = re.search(r'(?i)x-tidal-token[^A-Za-z0-9]+([A-Za-z0-9]{20,})', script)
            if not token_match:
                raise ScrapeError("Could not parse Tidal web token from assets.")
            cls._web_token = token_match[1]
            cls._web_token_fetched_at = time.time()
            return cls._web_token
        except requests.RequestException as e:
            raise ScrapeError("Failed to retrieve Tidal web token.") from e

    async def create_soup(self, url, params=None):
        """Run a GET request to Tidal's web JSON API for album data."""
        params = params or {}
        album_id = self.parse_release_id(url)

        for cc in get_tidal_regions_to_fetch():
            try:
                self.country_code = cc
                base_params = {**params, "countryCode": cc}
                data = await self.get_json(f"/albums/{album_id}", params=base_params, headers=self._headers())
                album_artists = self.normalize_artists(data.get("artists") or data.get("artist"))

                tracklist = await self._fetch_album_items(album_id, base_params)
                if not self._tracklist_has_artists(tracklist):
                    try:
                        fallback_tracklist = await self._fetch_album_tracks(album_id, base_params)
                    except ScrapeError:
                        fallback_tracklist = []
                    if fallback_tracklist:
                        tracklist = fallback_tracklist

                data["tracklist"] = [self._normalize_track_artists(track, album_artists) for track in tracklist]
                if not data["tracklist"] or not self._tracklist_has_artists(data["tracklist"]):
                    raise ScrapeError("Tidal album response did not include usable track artists.")

                return data
            except json.decoder.JSONDecodeError as e:
                raise ScrapeError("Tidal page did not return valid JSON.") from e
            except (KeyError, ScrapeError):
                pass
        raise ScrapeError(f"Failed to grab metadata for {url}.")


def get_tidal_regions_to_fetch():
    # TODO: maybe make this a validation
    if cfg.metadata.tidal.fetch_regions:
        return cfg.metadata.tidal.fetch_regions
    else:
        raise ScrapeError("No regions defined for Tidal to grab from")
