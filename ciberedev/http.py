from __future__ import annotations

import asyncio
import json
import logging
import re
import sys
import time
from asyncio import AbstractEventLoop
from io import BytesIO
from typing import TYPE_CHECKING, Any, Coroutine, Literal, Optional, TypeVar, Union
from urllib.parse import urlencode

import aiohttp
from aiohttp import ClientResponse, ClientSession
from aiohttp.client_exceptions import ClientConnectionError
from typing_extensions import Self

from . import __version__
from .errors import APIOffline, HTTPException, UnknownDataReturned, UnknownStatusCode
from .file import File
from .searching import SearchResult
from .types.image import AddImageText, ImageToAscii
from .types.random import RandomWordData
from .types.screenshot import ScreenshotData
from .types.searching import GetSearchResultData, SearchResultData

if TYPE_CHECKING:
    from .client import Client

    T = TypeVar("T")
    Response = Coroutine[Any, Any, T]

LOGGER = logging.getLogger("ciberedev.http")

__all__ = []


async def json_or_text(
    response: aiohttp.ClientResponse, /
) -> Union[dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
    except KeyError:
        pass

    return text


async def error_or_text(data: Union[dict, str]) -> str:
    if isinstance(data, dict):
        return data["error"]
    else:
        return data


class Route:
    __slots__ = ["method", "endpoint"]

    def __init__(
        self,
        *,
        method: Literal["POST", "GET"],
        endpoint: str,
    ):
        self.method = method
        self.endpoint = endpoint


class HTTPClient:
    _session: Optional[ClientSession]
    _client: Client
    _loop: Optional[AbstractEventLoop]
    latency: Optional[float]
    requests: int

    __slots__ = ["_session", "_client", "_loop", "user_agent", "latency", "requests"]

    def __init__(self, *, session: Optional[ClientSession], client: Client):
        self._session = session
        self._client = client
        self._loop: Optional[AbstractEventLoop] = None
        user_agent = "ciberedev.py (https://github.com/cibere/ciberedev.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent = user_agent.format(
            __version__, sys.version_info, aiohttp.__version__
        )

    async def ping(self) -> float:
        route = Route(method="GET", endpoint="https://api.cibere.dev/ping")

        before = time.perf_counter()
        await self.request(route)
        after = time.perf_counter()

        latency = after - before
        self.latency = latency
        return latency

    async def request(self, route: Route, **kwargs) -> Any:
        if self._session is None:
            self._session = ClientSession()
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        self.requests += 1

        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent
        url = route.endpoint
        endpoint = f"/{route.method.split('/')[-1]}"

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"

        for current_try in range(3):
            try:
                res = await self._session.request(
                    route.method, url, ssl=False, **kwargs
                )
                data = await json_or_text(res)
            except ClientConnectionError:
                raise APIOffline(endpoint)

            if 300 > res.status >= 200:
                return data
            elif res.status == 500:
                time = 2 * current_try

                LOGGER.warning(
                    "API returned a 500 status code at '%s'. Retrying in %s seconds",
                    endpoint,
                )
                await asyncio.sleep(time)
                continue
            elif res.status == 429:
                self._loop.create_task(self._client.on_ratelimit(endpoint))
                await asyncio.sleep(5)
                return await self.request(route)
            elif res.status == 502:
                raise APIOffline(endpoint)
            elif res.status == 400:
                error = await error_or_text(data)
                raise HTTPException(error)
            else:
                raise UnknownStatusCode(res.status)

    async def get_image_from_url(self, url: str) -> bytes:
        if self._session is None:
            self._session = ClientSession()
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        res = await self._session.get(url)
        if res.status == 200:
            return await res.read()
        else:
            txt: str = await json_or_text(res)  # type: ignore[PylancereportGeneralTypeIssues] # very wierd error that is false
            raise HTTPException(txt)

    def take_screenshot(self, url: str, delay: int) -> Response[ScreenshotData]:
        args = {"url": url, "delay": delay}
        route = Route(
            method="POST",
            endpoint="https://api.cibere.dev/screenshot",
        )

        return self.request(route, params=args)

    def get_search_results(
        self, query: str, amount: int
    ) -> Response[GetSearchResultData]:
        args = {"query": query, "amount": amount}
        route = Route(
            method="GET",
            endpoint="https://api.cibere.dev/search",
        )

        return self.request(route, params=args)

    def get_random_words(self, amount: int) -> Response[RandomWordData]:
        args = {"amount": str(amount)}
        route = Route(
            method="GET",
            endpoint="https://api.cibere.dev/random/word",
        )
        return self.request(route, params=args)

    def convert_image_to_ascii(
        self, url: str, width: Optional[int] = None
    ) -> Response[ImageToAscii]:
        args = {"url": url}
        if width:
            args["width"] = str(width)

        route = Route(
            method="GET",
            endpoint="https://api.cibere.dev/image/ascii",
        )
        return self.request(route, params=args)

    def add_text_to_image(
        self, url: str, text: str, color: tuple[int, int, int]
    ) -> Response[AddImageText]:
        data = {"url": url, "text": text, "color": list(color)}

        route = Route(
            method="GET",
            endpoint="https://api.cibere.dev/image/add-text",
        )

        return self.request(route)
