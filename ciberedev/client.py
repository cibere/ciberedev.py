import io
import os
from typing import Optional
from urllib.parse import urlencode

import validators
from aiohttp import ClientSession
from typing_extensions import Self

from .errors import (
    ClientAlreadyStarted,
    ClientNotStarted,
    InvalidAuthorizationGiven,
    InvalidFilePath,
    InvalidURL,
    NoAuthorizationGiven,
    UnableToConnect,
    UnknownEmbedField,
    UnknownError,
    UnknownMimeType,
)
from .screenshot import Screenshot
from .searching import SearchResult
from .utils import read_file


class Client:
    _session: ClientSession

    def __init__(self, *, session: Optional[ClientSession] = None):
        """Lets you create a client instance

        :session: an optional aiohttp session
        """

        self._session = session or ClientSession()
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

        await self._session.close()

    async def take_screenshot(
        self, url: str, /, *, delay: Optional[int] = 0
    ) -> Screenshot:
        """Takes a screenshot of the given url

        :url: the url you want a screenshot of
        :delay: the delay between opening the link and taking the actual picture

        :returns: ciberedev.screenshot.Screenshot
        """

        url = url.removeprefix("<").removesuffix(">")

        if not url.startswith("http"):
            url = f"http://{url}"

        if not validators.url(url):  # type: ignore
            raise InvalidURL(url)

        raw_data = {"url": url, "delay": delay, "mode": "short"}
        data = urlencode(raw_data)
        res = await self._session.post(
            f"https://api.cibere.dev/screenshot?{data}",
            ssl=False,
        )
        data = await res.json()

        if data["status_code"] == 200:
            screenshot = Screenshot(data=data)
            return screenshot
        else:
            if data["error"] == "I was unable to connect to the website.":
                raise UnableToConnect(url)
            elif data["error"] == "Invalid URL Given":
                raise InvalidURL(url)
            elif data["error"] == "Invalid Authorization":
                raise InvalidAuthorizationGiven()
            else:
                raise UnknownError(data["error"])

    async def search(self, query: str, amount: int = 5) -> list[SearchResult]:
        """Searches the web with the given query

        :query: what you want to search
        :amount: the amount of results you want

        :returns: [ciberedev.searching.SearchResult, ...]
        """

        data = {"query": query, "amount": amount}

        request = await self._session.get(
            f"https://api.cibere.dev/search?{urlencode(data)}", ssl=False
        )
        json = await request.json()
        results = []
        for result in json["results"]:
            search_result = SearchResult(data=result)
            results.append(search_result)
        return results
