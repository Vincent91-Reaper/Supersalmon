import re

import requests

from brucelee94.errors import ImageUploadFailed
from brucelee94.images.base import BaseImageUploader


class ImageUploader(BaseImageUploader):
    def _perform(self, file_, ext):
        url = "https://share.cyx.su/api/upload"
        resp = requests.post(url, files={"file": file_})
        if resp.status_code != requests.codes.ok:
            raise ImageUploadFailed(f"Failed. Status {resp.status_code}:\n{resp.content}")

        upload_url = self._extract_url(resp)
        if upload_url:
            return upload_url, None
        raise ImageUploadFailed(f"Missing image URL in response:\n{resp.content}")

    def _extract_url(self, resp):
        try:
            data = resp.json()
        except ValueError:
            data = None

        if isinstance(data, str):
            return self._normalize_url(data)

        if isinstance(data, dict):
            url = self._find_url(data)
            if url:
                return url

        text_match = re.search(r"https?://[^\s\"'<>]+", resp.text)
        if text_match:
            return text_match.group(0)
        return None

    def _find_url(self, value):
        if isinstance(value, str):
            return self._normalize_url(value)
        if isinstance(value, list):
            for item in value:
                url = self._find_url(item)
                if url:
                    return url
        if isinstance(value, dict):
            for key in ("url", "link", "href", "full_url", "download_url", "file"):
                if key in value:
                    url = self._find_url(value[key])
                    if url:
                        return url
            for item in value.values():
                url = self._find_url(item)
                if url:
                    return url
        return None

    def _normalize_url(self, value):
        if value.startswith("http://") or value.startswith("https://"):
            return value
        if value.startswith("/"):
            return f"https://share.cyx.su{value}"
        return None
