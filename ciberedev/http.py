from __future__ import annotations

import asyncio
import logging
import re
import time
from asyncio import AbstractEventLoop
from io import BytesIO
from typing import TYPE_CHECKING, Literal, Optional
from urllib.parse import urlencode

from aiohttp import ClientResponse, ClientSession
from aiohttp.client_exceptions import ClientConnectionError
from typing_extensions import Self

from .errors import (
    APIException,
    APIOffline,
    InvalidURL,
    UnableToConnect,
    UnknownDataReturned,
    UnknownError,
    UnknownStatusCode,
)
from .file import File
from .searching import SearchResult
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


class Route:
    __slots__ = ["method", "endpoint", "headers", "query_params"]

    def __init__(
        self,
        *,
        method: Literal["POST", "GET"],
        endpoint: str,
        headers: Optional[Headers] = None,
        query_params: Optional[QueryParams] = None,
    ):
        self.method = method
        self.endpoint = endpoint
        self.headers = headers or Headers()
        self.query_params = query_params or QueryParams()


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

    __slots__ = ["_session", "_client", "_loop"]

    def __init__(self, *, session: Optional[ClientSession], client: Client):
        self._session = session
        self._client = client
        self._loop: Optional[AbstractEventLoop] = None

    async def ping(self) -> int:
        route = Route(method="GET", endpoint="https://api.cibere.dev/ping")
        res = await self.request(route)
        return res.status

    async def request(self, route: Route) -> Response:
        if self._session is None:
            self._session = ClientSession()
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        self._client._requests += 1

        headers = route.headers.unpack()
        query_params = route.query_params.unpack()
        url = route.endpoint
        endpoint = f"/{route.method.split('/')[-1]}"

        if query_params:
            url += f"?{urlencode(query_params)}"

        LOGGER.debug("Request URL: %s", url)
        LOGGER.debug("Request Headers: %s", headers)
        LOGGER.debug("Request Query Params: %s", query_params)

        try:
            before = time.perf_counter()
            res = await self._session.request(
                route.method, url, headers=headers, ssl=False
            )
            after = time.perf_counter()
            response = await Response.create(aiohttp_response=res)
        except ClientConnectionError:
            raise APIOffline(endpoint)

        self._client._latency = after - before

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
        else:
            return response

    async def get_checkers_board(self, pattern: str) -> bytes:
        API_accepted_pattern = []
        for index, char in enumerate(pattern):
            if index in [0, 1, 2, 3, 8, 9, 10, 11, 16, 17, 18, 19, 24, 25, 26, 27]:
                API_accepted_pattern.extend(["_", char])
            else:
                API_accepted_pattern.extend([char, "_"])

        route = Route(
            method="GET",
            endpoint=f"https://api.cibere.dev/boardgame/checkers/{''.join(API_accepted_pattern)}",
        )
        response = await self.request(route)
        if response.status == 200:
            return await response.read()
        elif response.status == 400:
            raise APIException(response.json["error"])
        else:
            raise UnknownStatusCode(response.status)

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
        )

        response = await self.request(route)
        if response.status == 200:
            try:
                data = ScreenshotData(
                    link=response.json["link"], status_code=response.json["status_code"]
                )
            except KeyError:
                raise UnknownDataReturned("/screenshot")
        elif response.status == 400:
            if response.json["error"] == "Invalid URL Given":
                raise InvalidURL(url)
            elif response.json["error"] == "I was unable to connect to the website.":
                raise UnableToConnect(url)
            else:
                raise APIException(response.json["error"])
        else:
            raise UnknownStatusCode(response.status)

        link = data["link"]
        image_route = Route(method="GET", endpoint=link)
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
        )

        response = await self.request(route)
        if response.status == 200:
            try:
                data = GetSearchResultData(
                    results=response.json["results"],
                    status_code=response.json["status_code"],
                )
            except KeyError:
                raise UnknownDataReturned("/search")
        elif response.status == 400:
            if response.json["error"] == "Invalid 'amount' given, it must be an int":
                raise TypeError("'amount' must be an int")
            elif (
                response.json["error"]
                == "Invalid 'amount' given, can not be more than 10"
            ):
                raise TypeError("'amount' must be => 10")
            else:
                raise APIException(response.json["error"])
        else:
            raise UnknownStatusCode(response.status)

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
        )
        response = await self.request(route)
        if response.status == 200:
            try:
                data = RandomWordData(
                    words=response.json["words"],
                    status_code=response.json["status_code"],
                )
            except KeyError:
                raise UnknownDataReturned("/random/word")
        else:
            raise UnknownStatusCode(response.status)

        return data["words"]
