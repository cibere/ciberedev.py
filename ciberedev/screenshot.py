from typing import TypedDict


class RawScreenshotData(TypedDict):
    link: str
    status_code: int


class Screenshot:
    def __init__(self, *, data: RawScreenshotData):
        self.url = data.get("link")
