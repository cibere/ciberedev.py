from typing import TypedDict


class RawFileUploadData(TypedDict):
    file_id: str
    file_ext: str
    link: str
    status_code: int


MIMETYPES = {
    "png": "image/png",
    "jpg": "image/jpg",
    "gif": "image/gif",
    "mp4": "video/mp4",
    "mp3": "video/mp3",
    "pdf": "application/pdf",
}


class File:
    def __init__(self, *, data: RawFileUploadData):
        self.url = data.get("link")
        self.code = data.get("file_id")
