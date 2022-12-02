__all__ = ["SearchResult"]


class SearchResult:
    title: str
    description: str
    desc: str
    url: str

    __slots__ = ["title", "description", "desc", "url"]

    def __init__(self, *, data: dict):
        """Creates a SearchResult object.

        THIS SHOULD NOT BE CREATED MANUALLY, LET THE INTERNALS CREATE THEM

        Parameters
        -----------
        data: `dict`
            The raw search result data

        Attributes
        -----------
        title: `str`
            The search results title
        description: `str`
            the search results description
        desc: `str`
            alias for `SearchResult.description`
        url: `str`
            the search results url
        """

        self.title = data["title"]
        self.description = data["description"]
        self.desc = self.description
        self.url = data["url"]
