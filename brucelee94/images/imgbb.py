import requests

from brucelee94 import cfg
from brucelee94.errors import ImageUploadFailed
from brucelee94.images.base import BaseImageUploader


class ImageUploader(BaseImageUploader):
    def _perform(self, file_, ext):
        url = "https://api.imgbb.com/1/upload"
        params = {"key": cfg.image.imgbb_key}
        files = {"image": file_}
        resp = requests.post(url, params=params, files=files)
        if resp.status_code == requests.codes.ok:
            try:
                response = resp.json()
                data = response.get("data") or {}
                image_url = data.get("url") or data.get("display_url")
                if image_url:
                    return image_url, data.get("delete_url")
                raise ImageUploadFailed(f"Missing image URL in response:\n{resp.content}")
            except ValueError as e:
                raise ImageUploadFailed(f"Failed decoding body:\n{e}\n{resp.content}") from e
        raise ImageUploadFailed(f"Failed. Status {resp.status_code}:\n{resp.content}")
