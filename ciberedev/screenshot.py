from io import BytesIO
from typing import TypedDict


class Screenshot:
    def __init__(self, *, _bytes: BytesIO, url: str):
        self.url: str = url
        self.bytes: BytesIO = _bytes
