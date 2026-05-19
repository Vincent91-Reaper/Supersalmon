import re
import time

import requests

from brucelee94.errors import ScrapeError
from brucelee94.sources.base import BaseScraper, loop


class BeatportBase(BaseScraper):
    url = site_url = "https://beatport.com"
    api_url = "https://api.beatport.com"
    token_url = "https://www.beatport.com/api/auth/refresh-anon-token"
    search_url = "https://beatport.com/search/releases"
    api_search_url = "/v4/catalog/search/"
    release_format = "/release/{rls_name}/{rls_id}"
    regex = re.compile(r"^https?://(?:(?:www|classic)\.)?beatport\.com/release/.+?/(\d+)/?$")

    _token = None
    _token_expires = 0

    beatport_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.beatport.com",
        "Referer": "https://www.beatport.com/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
    }

    @classmethod
    def _api_headers(cls):
        return {**cls.beatport_headers, "Authorization": f"Bearer {cls._get_token()}"}

    @classmethod
    def _get_token(cls, force_refresh=False):
        if not force_refresh and cls._token and time.time() < cls._token_expires - 300:
            return cls._token

        try:
            response = requests.post(cls.token_url, headers=cls.beatport_headers, timeout=15)
        except requests.RequestException as e:
            raise ScrapeError("Failed to fetch Beatport anonymous token") from e

        if response.status_code != 200:
            raise ScrapeError(f"Failed to fetch Beatport anonymous token. Status code: {response.status_code}")

        try:
            data = response.json()
            cls._token = data["access_token"]
            try:
                expires_in = int(data.get("expires_in") or 3600)
            except (TypeError, ValueError):
                expires_in = 3600
            cls._token_expires = time.time() + expires_in
            return cls._token
        except (KeyError, TypeError, ValueError) as e:
            raise ScrapeError("Failed to parse Beatport anonymous token response") from e

    @classmethod
    def _api_get_sync(cls, url, params=None, retry=True):
        full_url = url if url.startswith("http") else f"{cls.api_url}{url}"
        try:
            response = requests.get(full_url, params=params, headers=cls._api_headers(), timeout=15)
        except requests.RequestException as e:
            raise ScrapeError(f"Failed to fetch Beatport API data from {full_url}") from e

        if response.status_code in {400, 401} and retry:
            cls._get_token(force_refresh=True)
            return cls._api_get_sync(url, params=params, retry=False)

        if response.status_code != 200:
            raise ScrapeError(f"Failed to fetch Beatport API data. Status code: {response.status_code}")

        try:
            return response.json()
        except ValueError as e:
            raise ScrapeError("Beatport API did not return JSON") from e

    async def api_get(self, url, params=None):
        return await loop.run_in_executor(None, lambda: self._api_get_sync(url, params=params))

    async def create_soup(self, url, params=None):
        """Fetch Beatport release metadata through Beatport's JSON API."""
        match = self.regex.match(url)
        if not match:
            raise ScrapeError("Invalid Beatport release URL")

        release_id = match[1]
        release = await self.api_get(f"/v4/catalog/releases/{release_id}/")
        tracks = await self._get_release_tracks(release_id)

        if not tracks:
            raise ScrapeError("Could not find Beatport track data")

        return {"state": {"data": {"results": self._compat_track_results(release, tracks)}}}

    async def _get_release_tracks(self, release_id):
        results = []
        next_url = f"/v4/catalog/releases/{release_id}/tracks/"
        params = {"per_page": 100}
        while next_url:
            response = await self.api_get(next_url, params=params)
            results.extend(response.get("results") or [])
            next_url = response.get("next")
            params = None
        return results

    @staticmethod
    def _compat_track_results(release, tracks):
        """Build the legacy shape expected by the existing Beatport tagger parser."""
        release_payload = {
            "id": release.get("id"),
            "name": release.get("name"),
            "image": release.get("image") or {},
            "label": release.get("label") or {},
        }
        compat_tracks = []
        for track in tracks:
            compat_tracks.append(
                {
                    **track,
                    "release": release_payload,
                    "catalog_number": release.get("catalog_number") or track.get("catalog_number"),
                    "new_release_date": release.get("new_release_date") or track.get("new_release_date"),
                }
            )
        return compat_tracks
