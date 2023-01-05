import logging
import re
from typing import Optional

from aiohttp import ClientSession
from typing_extensions import Self

from .errors import ClientAlreadyClosed
from .file import File
from .http import HTTPClient
from .searching import SearchResult

__all__ = ["Client"]

LOGGER = logging.getLogger(__name__)
URL_REGEX = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class Client:
    _http: HTTPClient
    _started: bool

    __slots__ = ["_http", "_started"]

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

    @property
    def latency(self) -> Optional[float]:
        """The latency between the client and the api.

        This variable stores the result of the last time `ciberedev.client.Client.ping` was called. By default it is `None`
        """

        return self._http.latency

    @property
    def requests(self) -> int:
        """The amount of requests sent to the api during the programs lifetime"""

        return self._http.requests

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
        if not re.match(URL_REGEX, url):
            raise TypeError("Invalid URL Given")

        data = await self._http.take_screenshot(url, delay)
        link = data["link"]
        fp = await self._http.get_image_from_url(link)

        file = File(raw_bytes=fp, url=link)
        return file

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

        data = await self._http.get_search_results(query, amount)

        final = []
        for raw_result in data["results"]:
            result = SearchResult(data=raw_result)
            final.append(result)

        return final

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

        data = await self._http.get_random_words(amount)
        return data["words"]

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

        if not re.match(URL_REGEX, url):
            raise TypeError("Invalid URL Given")

        data = await self._http.convert_image_to_ascii(url, width)
        art = data["msg"]
        return art

    async def add_text_to_image(
        self,
        *,
        image_url: str,
        text: str,
        text_color: Optional[tuple[int, int, int]] = None,
    ) -> File:
        """|coro|

        Adds text to a given image

        Parameters
        ----------
        image_url: `str`
            the images url
        text: `str`
            the text to be added
        text_color: tuple[`int`, `int`, `int`]
            the color to be added to the text

        Raises
        ----------
        UnknownError
            The api has returned an unknown error
        APIOffline
            I could not connect to the api

        Returns
        ----------
        ciberedev.file.File
            A file with the new image
        """

        color = text_color or (
            255,
            255,
            255,
        )
        if not re.match(URL_REGEX, image_url):
            raise TypeError("Invalid URL Given")
        for value in color:
            if value > 255:
                raise TypeError("Invalid color given")

        data = await self._http.add_text_to_image(image_url, text, color)
        url = data["link"]
        fp = await self._http.get_image_from_url(url)

        file = File(raw_bytes=fp, url=url)
        return file

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
