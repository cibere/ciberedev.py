from typing import Literal, Optional
from urllib.parse import urlencode

import validators
from aiohttp import ClientSession

from .errors import InvalidURL, UnableToConnect, UnknownError
from .screenshot import Screenshot
from .searching import SearchResult


class Parameters:
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
    def __init__(self, *, json: dict, status_code: int):
        self.data = json
        self.status = status_code


class HTTPClient:
    def __init__(self, *, session: ClientSession):
        self._session = session

    async def request(self, route: Route) -> Response:
        headers = route.headers.unpack()
        query_params = route.headers.unpack()
        url = route.endpoint

        if query_params:
            url += f"?{urlencode(query_params)}"

        res = await self._session.request(route.method, url, headers=headers)

        data = await res.json()
        response = Response(json=data, status_code=res.status)
        return response

    async def take_screenshot(self, url: str, delay: int) -> Screenshot:
        if not validators.url(url):  # type: ignore
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
        data = response.data

        if data["status_code"] == 200:
            screenshot = Screenshot(data=data)  # type: ignore
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

        results = []
        for result in response.data["results"]:
            search_result = SearchResult(data=result)
            results.append(search_result)
        return results
