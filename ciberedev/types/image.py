from typing import TypedDict


class ImageToAscii(TypedDict):
    msg: str
    status_code: int


class AddImageText(TypedDict):
    link: str
    status_code: int
