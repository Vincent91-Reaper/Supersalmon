import base64
import json
import re
import time

import requests

from brucelee94.errors import ScrapeError
from .base import BaseScraper, loop


TOKEN_REFRESH_BUFFER_SECONDS = 7 * 24 * 3600
BASE64_PADDING_MODULO = 4


class iTunesBase(BaseScraper):
    url = site_url = "https://itunes.apple.com"
    search_url = "https://itunes.apple.com/search"
    regex = re.compile(r"^https?://(itunes|music)\.apple\.com/(?:(\w{2,4})/)?album/(?:[^/]*/)?([^\?]+)")
    release_format = "/us/album/{rls_id}"
    _amp_token = None
    _amp_token_expires = 0

    @classmethod
    def parse_release_id(cls, url):
        match = cls.regex.search(url)
        if not match:
            raise ScrapeError("Invalid Apple Music URL.")
        return match[3].split("?")[0]

    @classmethod
    def parse_region(cls, url):
        match = cls.regex.search(url)
        return (match[2] if match and match[2] else "us").lower()

    async def create_soup(self, url, params=None):
        album_id = self.parse_release_id(url)
        region = self.parse_region(url)
        return await loop.run_in_executor(None, lambda: self.get_amp_album(album_id, region))

    def get_amp_album(self, album_id, region="us"):
        api_url = (
            f"https://amp-api.music.apple.com/v1/catalog/{region}/albums/{album_id}"
            "?include[songs]=artists&include=artists&platform=web"
        )
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"Bearer {self.get_amp_token()}",
                "Origin": "https://music.apple.com",
                "Referer": "https://music.apple.com/",
            },
            timeout=10,
        )
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ScrapeError("Apple AMP API did not return valid JSON.") from e
        if response.status_code != 200:
            raise ScrapeError(f"Apple AMP API failed with status {response.status_code}; see payload for details.", data)
        return data

    @classmethod
    def get_amp_token(cls):
        if cls._amp_token and time.time() < cls._amp_token_expires - TOKEN_REFRESH_BUFFER_SECONDS:
            return cls._amp_token
        try:
            html = requests.get("https://music.apple.com/us/new", timeout=10).text
            src_match = re.search(r'<script[^>]+src="([^"]*assets/index[^"]+)"', html)
            if not src_match:
                raise ScrapeError("Could not locate Apple Music AMP asset.")
            script_url = src_match[1]
            if script_url.startswith("/"):
                script_url = f"https://music.apple.com{script_url}"
            script = requests.get(script_url, timeout=10).text
            token_match = re.search(r"(eyJ[\w.-]+)", script)
            if not token_match:
                raise ScrapeError("Could not parse Apple Music AMP token.")
            token = token_match[1]
            cls._amp_token = token
            cls._amp_token_expires = cls._parse_jwt_expiry(token)
            return token
        except requests.RequestException as e:
            raise ScrapeError("Failed to retrieve Apple Music AMP token.") from e

    @staticmethod
    def _parse_jwt_expiry(token):
        try:
            payload = token.split(".")[1]
            # JWT payloads may omit base64 padding; this is the number of '=' chars
            # needed to make the payload length a multiple of 4 before decoding.
            payload += "=" * (-len(payload) % BASE64_PADDING_MODULO)
            decoded = base64.urlsafe_b64decode(payload.encode()).decode()
            return int(json.loads(decoded).get("exp", 0))
        except (IndexError, ValueError, json.JSONDecodeError):
            return 0
