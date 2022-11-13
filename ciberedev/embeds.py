from typing import TypedDict

from typing_extensions import NotRequired

EmbedFields = ["title", "description", "author", "image", "thumbnail", "url", "color"]


class EmbedData(TypedDict):
    title: NotRequired[str]
    description: NotRequired[str]
    author: NotRequired[str]
    image: NotRequired[str]
    thumbnail: NotRequired[str]
    url: NotRequired[str]
    color: NotRequired[str]


class RawEmbedData(TypedDict):
    status_code: int
    link: str
    code: str


class Embed:
    def __init__(self, *, data: RawEmbedData):
        self.url = data.get("link")
        self.code = data.get("code")
