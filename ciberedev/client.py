import logging
from typing import Optional

from aiohttp import ClientSession
from typing_extensions import Self

from .checkers import CheckersGame
from .errors import ClientAlreadyClosed
from .file import File
from .http import HTTPClient
from .searching import SearchResult

__all__ = ["Client"]
LOGGER = logging.getLogger("ciberedev")


class Client:
    _http: HTTPClient
    _started: bool
    _requests: int
    _latency: float

    __slots__ = ["_http", "_started", "_requests", "_latency"]

    def __init__(self, *, session: Optional[ClientSession] = None):
        """Lets you create a client instance

        Parameters
        ----------
        session: Optional[`aiohttp.ClientSession`]
            an optional aiohttp client session that the internals will use for API calls

        Attributes
        ----------
        latency: `float`
            The latency between the client and the api.
        requests: `int`
            The amount of requests sent to the api during the programs lifetime
        """

        self._http = HTTPClient(session=session, client=self)
        self._started = True
        self._requests = 0
        self._latency = 0.0

    @property
    def latency(self) -> float:
        """The latency between the client and the api.

        This will be '0.0' until the first API call.
        This will be updated after every API call.
        """

        return self._latency

    @property
    def requests(self) -> int:
        """The amount of requests sent to the api during the programs lifetime"""

        return self._requests

    def is_closed(self) -> bool:
        """Returns a bool depending on if the client has been closed or not

        Returns
        ----------
        bool
            True if the client is closed, False if its not been closed
        """

        return not self._started

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, exception_type, exception_value, exception_traceback
    ) -> None:
        await self.close()

    async def create_checkers_game(self, pattern: Optional[str] = None) -> CheckersGame:
        """Creates a checkers game instance

        Parameters
        ----------
        pattern: Optional[`str`]
            A pattern that is used to generate the board. By default it is the default board setup

        Raises
        ----------
        InvalidPattern
            The given pattern is invalid

        Returns
        ----------
        ciberedev.checkers.CheckersGame
        """

        if pattern:
            game = CheckersGame.from_pattern(pattern, http_client=self._http)
        else:
            game = CheckersGame(http_client=self._http)
        return game

    async def on_ratelimit(self, endpoint: str) -> None:
        """|coro|

        This function is auto triggered when it hits a rate limit.

        When overriding this, you can call the super init if you still want the library to send the logs

        Parameters
        ----------
        endpoint: `str`
            the endpoint the ratelimit was hit at. Ex: '/screenshot'
        """

        LOGGER.warning(
            f"We are being ratelimited at '{endpoint}'. Trying again in 5 seconds"
        )

    async def close(self) -> None:
        """|coro|

        Closes the aiohttp session

        Raises
        ----------
        ClientAlreadyClosed
            This is raised when you already closed the client
        """

        if not self._started:
            raise ClientAlreadyClosed()

        if self._http._session:
            await self._http._session.close()

    async def take_screenshot(self, url: str, /, *, delay: int = 0) -> File:
        """|coro|

        Takes a screenshot of the given url

        Parameters
        ----------
        url: `str`
            The url you want to be screenshotted
        delay: Optional[`int`]
            The delay between going to the website, and taking the screenshot


        Raises
        ----------
        UnableToConnect
            If the api is unable to connect to the provided website
        InvalidURL
            If the url given is invalid
        UnknownError
            The api has returned an unknown error
        APIOffline
            I could not connect to the api

        Returns
        ----------
        ciberedev.file.File
            A file object of your screenshot
        """

        url = url.removeprefix("<").removesuffix(">")

        if not url.startswith("http"):
            url = f"http://{url}"

        return await self._http.take_screenshot(url, delay)

    async def get_search_results(
        self, query: str, /, *, amount: int = 5
    ) -> list[SearchResult]:
        """|coro|

        Searches the web with the given query

        Parameters
        ----------
        query: `str`
            The query of your search
        amount: Optional[`int`]
            The amount of results you want. Defaults to 5

        Raises
        ----------
        UnknownError
            The api has returned an unknown error
        APIOffline
            I could not connect to the api

        Returns
        ----------
        List[ciberedev.searching.SearchResult]
            A list of your search results
        """

        return await self._http.get_search_results(query, amount)

    async def get_random_words(self, amount: int, /) -> list[str]:
        """|coro|

        Gives you random words

        Parameters
        ----------
        amount: `int`
            the amount of random words you want

        Raises
        ----------
        UnknownError
            The api has returned an unknown error
        APIOffline
            I could not connect to the api

        Returns
        ----------
        List[`str`]
            the random words that have been generated
        """

        return await self._http.get_random_words(amount)
