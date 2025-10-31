from random import choice

import requests

from brucelee94.constants import UAGENTS
from brucelee94.errors import ImageUploadFailed
from brucelee94.images.base import BaseImageUploader

HEADERS = {
    "User-Agent": choice(UAGENTS),
    "referrer": "https://catbox.moe/",
}


class ImageUploader(BaseImageUploader):
    def _perform(self, file_, ext):
        data = {
            "reqtype": "fileupload",
            "userhash": "",
        }
        url = "https://catbox.moe/user/api.php"
        files = {"fileToUpload": file_}
        resp = requests.post(url, headers=HEADERS, data=data, files=files)
        if resp.status_code == requests.codes.ok:
            try:
                return resp.text, None
            except ValueError as e:
                raise ImageUploadFailed(f"Failed decoding body:\n{e}\n{resp.content}") from e
        else:
            raise ImageUploadFailed(f"Failed. Status {resp.status_code}:\n{resp.content}")
