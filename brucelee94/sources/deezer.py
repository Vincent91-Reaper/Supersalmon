import asyncio
import json
import re
from json.decoder import JSONDecodeError
from random import choice

import requests

from brucelee94.constants import UAGENTS
from brucelee94.errors import ScrapeError
from brucelee94.sources.base import BaseScraper

loop = asyncio.get_event_loop()

HEADERS = {
    "User-Agent": choice(UAGENTS),
    "Content-Language": "en-US",
    "Cache-Control": "max-age=0",
    "Accept": "*/*",
    "Accept-Charset": "utf-8,ISO-8859-1;q=0.7,*;q=0.3",
    "Accept-Language": "en",
}


class DeezerBase(BaseScraper):
    url = "https://api.deezer.com"
    site_url = "https://www.deezer.com"
    regex = re.compile(r"^https*:\/\/.*?deezer\.com.*?\/(?:[a-z]+\/)?(album|playlist|track)\/([0-9]+)")
    release_format = "/album/{rls_id}"

    def __init__(self):
        self.country_code = None
        super().__init__()

        self._csrf_token = None
        self._login_csrf_token = None
        self._session = None

    @property
    def sesh(self):
        if self._session:
            return self._session

        self._session = requests.Session()
        return self._session

    @property
    def api_token(self):
        if self._csrf_token:
            return self._csrf_token

        params = {"api_version": "1.0", "api_token": "null", "input": "3"}
        response = self.sesh.get(
            "https://www.deezer.com/ajax/gw-light.php",
            params={"method": "deezer.getUserData", **params},
            headers=HEADERS,
        )
        try:
            check_data = json.loads(response.text)
            self._csrf_token = check_data["results"]["checkForm"]
            self._login_csrf_token = check_data["results"]["checkFormLogin"]
        except (JSONDecodeError, KeyError):
            pass
        return self._csrf_token

    @classmethod
    def parse_release_id(cls, url):
        return cls.regex.search(url)[2]

    async def create_soup(self, url, params=None):
        """Run Deezer's web album API and public API for complete album metadata."""
        params = params or {}
        album_id = self.parse_release_id(url)
        try:
            public_data = await self.get_json(f"/album/{album_id}", params=params, headers=HEADERS)
            page_data = await loop.run_in_executor(None, lambda: self.get_page_album(album_id))
            album_data = page_data["results"]["DATA"]
            songs = page_data["results"]["SONGS"]["data"]

            public_data.update(
                {
                    "title": album_data.get("ALB_TITLE") or public_data.get("title"),
                    "release_date": album_data.get("DIGITAL_RELEASE_DATE") or public_data.get("release_date"),
                    "release_date_original": album_data.get("ORIGINAL_RELEASE_DATE"),
                    "copyright": album_data.get("COPYRIGHT"),
                    "label": album_data.get("LABEL_NAME") or public_data.get("label"),
                    "upc": album_data.get("UPC") or public_data.get("upc"),
                    "record_type": (album_data.get("TYPE") or public_data.get("record_type") or "").lower(),
                    "tracklist": songs,
                    "cover_xl": self.get_cover_from_code(album_data.get("ALB_PICTURE")) or public_data.get("cover_xl"),
                    "_deezer_page_album": album_data,
                }
            )
            return public_data
        except json.decoder.JSONDecodeError as e:
            raise ScrapeError("Deezer page did not return valid JSON.") from e
        except (KeyError, ScrapeError) as e:
            raise ScrapeError(f"Failed to grab metadata for {url}.") from e

    def get_page_album(self, album_id):
        params = {"api_version": "1.0", "api_token": self.api_token or "", "input": "3"}
        response = self.sesh.post(
            "https://www.deezer.com/ajax/gw-light.php",
            params={"method": "deezer.pageAlbum", **params},
            data=json.dumps({"alb_id": album_id, "header": True, "lang": "en", "tab": 0}),
            headers={**HEADERS, "Content-Type": "application/json"},
            timeout=10,
        )
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ScrapeError("Deezer pageAlbum did not return valid JSON.") from e
        if response.status_code != 200 or data.get("error"):
            raise ScrapeError(f"Deezer pageAlbum failed with status {response.status_code}; see payload for details.", data.get("error"))
        return data

    async def get_internal_api_data(self, url, params=None):
        """Deezer puts some things in an api that isn't public facing.
        Like track information and album art before a release is available.
        """
        track_data = await loop.run_in_executor(None, lambda: self.sesh.get(self.site_url + url, params=(params or {})))
        r = re.search(
            r"window.__DZR_APP_STATE__ = ({.*?}})</script>",
            track_data.text.replace("\n", ""),
        )
        if not r:
            raise ScrapeError("Failed to scrape track data.")
        raw = re.sub(r"{(\s*)type\: +\'([^\']+)\'", r'{\1type: "\2"', r[1])
        raw = re.sub("\t+([^:]+): ", r'"\1":', raw)
        return json.loads(raw)

    def get_tracks(self, internal_data):
        return internal_data["SONGS"]["data"]

    def get_cover(self, internal_data):
        "This uses a hardcoded url. Hope the dns url doesn't change."
        return self.get_cover_from_code(internal_data["DATA"]["ALB_PICTURE"])

    def get_cover_from_code(self, artwork_code):
        if not artwork_code:
            return None
        return f"https://e-cdns-images.dzcdn.net/images/cover/{artwork_code}/1000x1000-000000-100-0-0.jpg"
