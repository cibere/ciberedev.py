import logging
from typing import Optional

from aiohttp import ClientSession
from typing_extensions import Self

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

        This variable stores the result of the last time `ciberedev.client.Client.ping` was called. By default it is `0.0`
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
        if delay > 20:
            raise TypeError("Delay must be below 20")
        if delay < 0:
            raise TypeError("Delay can not be in the negatives")

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

    async def convert_image_to_ascii(
        self, url: str, /, *, width: Optional[int] = None
    ) -> str:
        """|coro|

        Converts the given image to ascii art

        Parameters
        ----------
        url: `str`
            the images url
        width: Optional[`int`]
            the ascii arts width

        Raises
        ----------
        UnknownError
            The api has returned an unknown error
        APIOffline
            I could not connect to the api

        Returns
        ----------
        str
            the ascii art"""

        return await self._http.convert_image_to_ascii(url, width)

    async def ping(self) -> float:
        """|coro|

        Pings the api

        Raises
        ----------
        UnknownError
            The api has returned an unknown error
        APIOffline
            I could not connect to the api

        Returns
        ----------
        float
            the latency. Multiply by 1000 to convert to ms
        """

        return await self._http.ping()
