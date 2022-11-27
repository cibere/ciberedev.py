from typing import Optional
from urllib.parse import urlencode

import validators
from aiohttp import ClientSession
from typing_extensions import Self

from .errors import (
    ClientNotStarted,
    InvalidAuthorizationGiven,
    InvalidURL,
    UnableToConnect,
    UnknownError,
)
from .http import HTTPClient
from .screenshot import Screenshot
from .searching import SearchResult


class Client:
    _http: HTTPClient

    def __init__(self, *, session: Optional[ClientSession] = None):
        """Lets you create a client instance

        :session: an optional aiohttp session
        """

        self._http = HTTPClient(session=session or ClientSession())
        self._started = True

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, exception_type, exception_value, exception_traceback
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Closes the client session"""

        if not self._started:
            raise ClientNotStarted()

        await self._http._session.close()

    async def take_screenshot(self, url: str, /, *, delay: int = 0) -> Screenshot:
        """Takes a screenshot of the given url

        :url: the url you want a screenshot of
        :delay: the delay between opening the link and taking the actual picture

        :returns: ciberedev.screenshot.Screenshot
        """

        url = url.removeprefix("<").removesuffix(">")

        if not url.startswith("http"):
            url = f"http://{url}"

        return await self._http.take_screenshot(url, delay)

    async def search(self, query: str, amount: int = 5) -> list[SearchResult]:
        """Searches the web with the given query

        :query: what you want to search
        :amount: the amount of results you want

        :returns: [ciberedev.searching.SearchResult, ...]
        """

        return await self._http.get_search_results(query, amount)
