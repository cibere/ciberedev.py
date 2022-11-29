from typing_extensions import TypedDict

__all__ = ["SearchResult"]


class RawSearchResult(TypedDict):
    title: str
    description: str
    url: str


class SearchResult:
    def __init__(self, *, data: dict):
        self._raw_data: RawSearchResult = RawSearchResult(
            title=data["title"], description=data["description"], url=data["url"]
        )

    @property
    def title(self) -> str:
        """The search results title"""

        return self._raw_data["title"]

    @property
    def description(self) -> str:
        """The search results description"""

        return self._raw_data["description"]

    @property
    def desc(self) -> str:
        """Alias for description"""

        return self.description

    @property
    def url(self) -> str:
        """The search results url"""

        return self._raw_data["url"]
