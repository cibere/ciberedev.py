from typing import TypedDict


class SearchResultData(TypedDict):
    title: str
    description: str
    url: str


class GetSearchResultData(TypedDict):
    results: list[SearchResultData]
    status_code: int
