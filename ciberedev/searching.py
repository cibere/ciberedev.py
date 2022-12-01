__all__ = ["SearchResult"]


class SearchResult:
    title: str
    description: str
    desc: str
    url: str

    __slots__ = ["title", "description", "desc", "url"]

    def __init__(self, *, data: dict):
        """Creates a SearchResult object.

        THIS SHOULD NOT BE CREATED MANUALLY, LET CIBEREDEV'S INTERNALS CREATE THEM
        """

        self.title = data["title"]
        "The search results title"

        self.description = data["description"]
        "The search results description"

        self.desc = self.description
        "Alias for `ciberedev.searching.SearchResult.description`"

        self.url = data["url"]
        "The search results url"
