from __future__ import annotations

import asyncio
import logging
import re
import sys
import time
from asyncio import AbstractEventLoop
from io import BytesIO
from typing import TYPE_CHECKING, Any, Literal, Optional, Union
from urllib.parse import urlencode

import aiohttp
from aiohttp import ClientResponse, ClientSession
from aiohttp.client_exceptions import ClientConnectionError
from typing_extensions import Self

from . import __version__
from .errors import (
    APIOffline,
    HTTPException,
    InvalidURL,
    UnableToConnect,
    UnableToConvertToImage,
    UnknownDataReturned,
    UnknownStatusCode,
)
from .file import File
from .searching import SearchResult
from .types.image import AddImageText, ImageToAscii
from .types.random import RandomWordData
from .types.screenshot import ScreenshotData
from .types.searching import GetSearchResultData, SearchResultData

if TYPE_CHECKING:
    from .client import Client

LOGGER = logging.getLogger("ciberedev.http")

__all__ = []


URL_REGEX = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class Parameters:
    __slots__ = ["_internal"]

    def __init__(self):
        self._internal = {}

    def __getitem__(self, key: str) -> Optional[str]:
        return self._internal.get(key)

    def __setitem__(self, key: str, value: str) -> None:
        self._internal[key] = value

    def unpack(self) -> dict:
        return self._internal


class QueryParams(Parameters):
    pass


class Headers(Parameters):
    pass


class JSONData(Parameters):
    def __setitem__(self, key: str, value: Union[str, dict, list]) -> None:
        self._internal[key] = value


class Route:
    __slots__ = ["method", "endpoint", "headers", "query_params", "data", "error_index"]

    def __init__(
        self,
        *,
        method: Literal["POST", "GET"],
        endpoint: str,
        headers: Optional[Headers] = None,
        query_params: Optional[QueryParams] = None,
        data: Optional[JSONData] = None,
        error_index: dict[str, Exception],
    ):
        self.method = method
        self.endpoint = endpoint
        self.headers = headers or Headers()
        self.query_params = query_params or QueryParams()
        self.data = data or JSONData()
        self.error_index = error_index


class Response:
    __slots__ = ["original", "read", "json", "get_json", "status", "text"]

    def __init__(self, *, aiohttp_response: ClientResponse):
        self.original: ClientResponse = aiohttp_response
        self.text = aiohttp_response.text
        self.read = aiohttp_response.read
        self.get_json = aiohttp_response.json
        self.json: dict = {}
        self.status: int = aiohttp_response.status

    @classmethod
    async def create(cls, *, aiohttp_response: ClientResponse) -> Self:
        self = cls(aiohttp_response=aiohttp_response)

        LOGGER.debug("Recieved Status Code: %s", aiohttp_response.status)

        try:
            self.json = await aiohttp_response.json()
        except:
            LOGGER.debug("Recieved Data: Not Json")
        finally:
            LOGGER.debug("Recieved Data: %s", self.json)
        return self


class HTTPClient:
    _session: Optional[ClientSession]
    _client: Client
    _loop: Optional[AbstractEventLoop]

    __slots__ = ["_session", "_client", "_loop", "user_agent"]

    def __init__(self, *, session: Optional[ClientSession], client: Client):
        self._session = session
        self._client = client
        self._loop: Optional[AbstractEventLoop] = None
        user_agent = "ciberedev.py (https://github.com/cibere/ciberedev.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent = user_agent.format(
            __version__, sys.version_info, aiohttp.__version__
        )

    async def ping(self) -> float:
        route = Route(
            method="GET", endpoint="https://api.cibere.dev/ping", error_index={}
        )

        before = time.perf_counter()
        await self.request(route)
        after = time.perf_counter()

        latency = after - before
        self._client._latency = latency
        return latency

    async def request(self, route: Route) -> Response:
        if self._session is None:
            self._session = ClientSession()
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        self._client._requests += 1

        headers = route.headers.unpack()
        headers["User-Agent"] = self.user_agent
        query_params = route.query_params.unpack()
        data = route.data.unpack()
        url = route.endpoint
        endpoint = f"/{route.method.split('/')[-1]}"

        if query_params:
            url += f"?{urlencode(query_params)}"

        LOGGER.debug("Request URL: %s", url)
        LOGGER.debug("Request Headers: %s", headers)
        LOGGER.debug("Request Query Params: %s", query_params)

        args: dict[str, Any] = {"ssl": False}

        if headers:
            args["headers"] = headers
        if data:
            args["json"] = data

        try:
            res = await self._session.request(route.method, url, **args)
            response = await Response.create(aiohttp_response=res)
        except ClientConnectionError:
            raise APIOffline(endpoint)

        if res.status == 500:
            LOGGER.warning(
                "API returned a 500 status code at '%s'. Retrying in 5 seconds",
                endpoint,
            )
            await asyncio.sleep(5)
            return await self.request(route)
        elif res.status == 429:
            self._loop.create_task(self._client.on_ratelimit(endpoint))
            await asyncio.sleep(5)
            return await self.request(route)
        elif res.status == 502:
            raise APIOffline(endpoint)
        elif res.status == 400:
            er = response.json["error"]
            error = route.error_index.get(er, HTTPException(er))
            raise error
        elif 300 > res.status >= 200:
            return response
        else:
            raise UnknownStatusCode(res.status)

    async def take_screenshot(self, url: str, delay: int) -> File:
        if not re.match(URL_REGEX, url) is not None:
            raise InvalidURL(url)

        query_params = QueryParams()
        query_params["url"] = url
        query_params["delay"] = str(delay)
        route = Route(
            method="POST",
            endpoint="https://api.cibere.dev/screenshot",
            query_params=query_params,
            error_index={
                "Invalid URL Given": InvalidURL(url),
                "I was unable to connect to the website.": UnableToConnect(url),
            },
        )

        response = await self.request(route)
        try:
            data = ScreenshotData(
                link=response.json["link"], status_code=response.json["status_code"]
            )
        except KeyError:
            raise UnknownDataReturned("/screenshot")

        link = data["link"]
        image_route = Route(method="GET", endpoint=link, error_index={})
        res = await self.request(image_route)
        _bytes = BytesIO(await res.read())
        file = File(raw_bytes=_bytes.read(), url=link)
        return file

    async def get_search_results(self, query: str, amount: int) -> list[SearchResult]:
        query_params = QueryParams()
        query_params["query"] = query
        query_params["amount"] = str(amount)
        route = Route(
            method="GET",
            endpoint="https://api.cibere.dev/search",
            query_params=query_params,
            error_index={
                "Invalid 'amount' given, it must be an int": TypeError(
                    "'amount' must be an int"
                ),
                "Invalid 'amount' given, can not be more than 10": TypeError(
                    "'amount' must be => 10"
                ),
            },
        )

        response = await self.request(route)
        try:
            data = GetSearchResultData(
                results=response.json["results"],
                status_code=response.json["status_code"],
            )
        except KeyError:
            raise UnknownDataReturned("/search")

        results = []
        raw_results = data["results"]
        for result in raw_results:
            try:
                result = SearchResultData(
                    title=result["title"],
                    description=result["description"],
                    url=result["url"],
                )
            except KeyError:
                raise UnknownDataReturned("/search")

            search_result = SearchResult(data=result)
            results.append(search_result)
        return results

    async def get_random_words(self, amount: int) -> list[str]:
        query_params = QueryParams()
        query_params["amount"] = str(amount)
        route = Route(
            method="GET",
            endpoint="https://api.cibere.dev/random/word",
            query_params=query_params,
            error_index={},
        )
        response = await self.request(route)
        try:
            data = RandomWordData(
                words=response.json["words"],
                status_code=response.json["status_code"],
            )
        except KeyError:
            raise UnknownDataReturned("/random/word")

        return data["words"]

    async def convert_image_to_ascii(
        self, url: str, width: Optional[int] = None
    ) -> str:
        query_params = QueryParams()
        query_params["url"] = url
        if width:
            query_params["width"] = str(width)

        route = Route(
            method="GET",
            endpoint="https://api.cibere.dev/image/ascii",
            query_params=query_params,
            error_index={
                "Invalid width given": TypeError("Invalid width given"),
                "Invalid URL Given": InvalidURL(url),
                "Could not convert to image": UnableToConnect(url),
            },
        )
        response = await self.request(route)
        try:
            data = ImageToAscii(
                msg=response.json["msg"],
                status_code=response.json["status_code"],
            )
        except KeyError:
            raise UnknownDataReturned("/image/ascii")
        return data["msg"]

    async def add_text_to_image(
        self, url: str, text: str, color: tuple[int, int, int]
    ) -> File:
        if not re.match(URL_REGEX, url):
            raise InvalidURL(url)
        for value in color:
            if value > 255:
                raise TypeError("Invalid color given")

        data = JSONData()
        data["url"] = url
        data["text"] = text
        data["color"] = list(color)

        route = Route(
            method="GET",
            endpoint="https://api.cibere.dev/image/add-text",
            data=data,
            error_index={},
        )

        response = await self.request(route)
        try:
            data = ScreenshotData(
                link=response.json["link"], status_code=response.json["status_code"]
            )
        except KeyError:
            raise UnknownDataReturned("/screenshot")

        link = data["link"]
        image_route = Route(method="GET", endpoint=link, error_index={})
        res = await self.request(image_route)
        _bytes = BytesIO(await res.read())
        file = File(raw_bytes=_bytes.read(), url=link)
        return file
