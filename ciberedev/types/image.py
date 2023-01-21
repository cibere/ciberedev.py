from typing import TypedDict


class BaseImage(TypedDict):
    link: str
    status_code: int


class ImageToAscii(TypedDict):
    msg: str
    status_code: int


class AddImageText(BaseImage):
    pass


class Laugh(BaseImage):
    pass
