import asyncio
import logging
from typing import Optional

from aiohttp import ClientSession
from typing_extensions import Self

from .errors import ClientNotStarted
from .http import HTTPClient
from .screenshot import Screenshot
from .searching import SearchResult

__all__ = ["Client"]
LOGGER = logging.getLogger("ciberedev")


class Client:
    _http: HTTPClient
    __slots__ = ["_http", "_started", "_requests"]

    def __init__(self, *, session: Optional[ClientSession] = None):
        """Lets you create a client instance

        :session: an optional aiohttp session
        """

        self._http = HTTPClient(session=session, client=self)
        self._started = True
        self._requests = 0

    @property
    def requests(self) -> int:
        """The amount of requests sent to the api during the programs lifetime"""

        return self._requests

    def is_closed(self) -> bool:
        """Returns a bool depending on if the client has been closed or not"""

        return not self._started

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, exception_type, exception_value, exception_traceback
    ) -> None:
        await self.close()

    async def on_ratelimit(self, endpoint: str) -> None:
        """This function is auto triggered when it hits a rate limit."""

        LOGGER.warning(
            f"We are being ratelimited at '{endpoint}'. Trying again in 5 seconds"
        )

    async def close(self) -> None:
        """Closes the client session"""

        if not self._started:
            raise ClientNotStarted()

        if self._http._session:
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

    async def get_search_results(
        self, query: str, /, *, amount: int = 5
    ) -> list[SearchResult]:
        """Searches the web with the given query

        :query: what you want to search
        :amount: the amount of results you want

        :returns: [ciberedev.searching.SearchResult, ...]
        """

        return await self._http.get_search_results(query, amount)
