from typing import TypedDict


class RawPasteData(TypedDict):
    url: str
    code: str
    status_code: int
    message: str


class Paste:
    def __init__(self, *, data: RawPasteData):
        self.url = data.get("url")
        self.code = data.get("code")