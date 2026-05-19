import json
import re
import time

import requests

from brucelee94 import cfg
from brucelee94.errors import ScrapeError
from brucelee94.sources.base import BaseScraper


APP_ID_CACHE_DURATION_SECONDS = 86400


class QobuzBase(BaseScraper):
    url = "https://www.qobuz.com/api.json/0.2"
    site_url = "https://www.qobuz.com"
    regex = re.compile(
        r"^https?://(?:www\.|play\.)?qobuz\.com/(?:(?:.+?/)?album/(?:.+?/)?|album/(?:-/)?)([a-zA-Z0-9]+)/?$"
    )
    release_format = "/album/get?album_id={rls_id}"
    get_params = {}
    _dynamic_app_id = None
    _dynamic_app_id_fetched_at = 0

    @classmethod
    def get_app_id(cls):
        if cfg.metadata.qobuz.app_id:
            return cfg.metadata.qobuz.app_id
        if cls._dynamic_app_id and time.time() - cls._dynamic_app_id_fetched_at < APP_ID_CACHE_DURATION_SECONDS:
            return cls._dynamic_app_id
        try:
            html = requests.get("https://open.qobuz.com", timeout=10).text
            src_match = re.search(r'<script[^>]+src="([^"]*main\.js[^"]*)"', html)
            if not src_match:
                raise ScrapeError("Could not locate Qobuz web app asset.")
            script_url = src_match[1]
            if script_url.startswith("/"):
                script_url = f"https://open.qobuz.com{script_url}"
            script = requests.get(script_url, timeout=10).text
            token_match = re.search(r"app_id:.([A-Za-z0-9]+)", script)
            if not token_match:
                token_match = re.search(r"app_id[\"']?\s*[:=]\s*[\"']([A-Za-z0-9]+)", script)
            if not token_match:
                raise ScrapeError("Could not parse Qobuz app id from web assets.")
            cls._dynamic_app_id = token_match[1]
            cls._dynamic_app_id_fetched_at = time.time()
            return cls._dynamic_app_id
        except requests.RequestException as e:
            raise ScrapeError("Failed to retrieve Qobuz app id.") from e

    @classmethod
    def headers(cls):
        headers = {"X-App-Id": cls.get_app_id()}
        if cfg.metadata.qobuz.user_auth_token:
            headers["X-User-Auth-Token"] = cfg.metadata.qobuz.user_auth_token
        return headers

    async def create_soup(self, url, params=None):
        try:
            rls_id = self.regex.match(url)[1]
            return await self.get_json(self.release_format.format(rls_id=rls_id), params=params, headers=self.headers())
        except json.decoder.JSONDecodeError as e:
            raise ScrapeError("Qobuz page did not return valid JSON.") from e
        except (AttributeError, IndexError) as e:
            raise ScrapeError("Invalid Qobuz URL.") from e
