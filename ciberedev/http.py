from __future__ import annotations

import asyncio
import logging
import re
from asyncio import AbstractEventLoop
from io import BytesIO
from typing import TYPE_CHECKING, Literal, Optional, Union
from urllib.parse import urlencode

from aiohttp import ClientResponse, ClientSession
from aiohttp.client_exceptions import ClientConnectionError

from .errors import APIOffline, InvalidURL, UnableToConnect, UnknownError
from .screenshot import Screenshot
from .searching import SearchResult

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


class HTTPClient:
    _session: Optional[ClientSession]
    _client: Client
    _loop: Optional[AbstractEventLoop]
    __slots__ = ["_session", "_client", "_loop"]

    def __init__(self, *, session: Optional[ClientSession], client: Client):
        self._session = session
        self._client = client
        self._loop: Optional[AbstractEventLoop] = None

    async def request(self, route: Route) -> ClientResponse:
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
            res = await self._session.request(
                route.method, url, headers=headers, ssl=False
            )
        except ClientConnectionError:
            raise APIOffline(endpoint)

        LOGGER.debug("Recieved Status Code: %s", res.status)
        LOGGER.debug("Recieved Headers: %s", dict(res.headers))

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
        else:
            return res

    async def take_screenshot(self, url: str, delay: int) -> Screenshot:
        if not re.match(URL_REGEX, "http://www.example.com") is not None:
            raise InvalidURL(url)

        query_params = QueryParams()
        query_params["url"] = url
        query_params["delay"] = str(delay)
        route = Route(
            method="POST",
            endpoint="https://api2.cibere.dev/screenshot",
            query_params=query_params,
        )

        response = await self.request(route)
        data = await response.json()
        LOGGER.debug("Recieved Data: %s", data)

        if data["status_code"] == 200:
            image_route = Route(method="GET", endpoint=data["link"])
            res = await self.request(image_route)
            _bytes = BytesIO(await res.read())
            screenshot = Screenshot(_bytes=_bytes, url=data["link"])
            return screenshot
        else:
            if data["error"] == "I was unable to connect to the website.":
                raise UnableToConnect(url)
            elif data["error"] == "Invalid URL Given":
                raise InvalidURL(url)
            else:
                raise UnknownError(data["error"])

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
        data = await response.json()
        LOGGER.debug("Recieved Data: %s", data)

        results = []
        for result in data["results"]:
            search_result = SearchResult(data=result)
            results.append(search_result)
        return results
