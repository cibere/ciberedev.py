import io
import os
from typing import Optional
from urllib.parse import urlencode

import validators
from aiohttp import ClientSession
from typing_extensions import Self

from .authorization import Authorization
from .embeds import Embed, EmbedData, EmbedFields
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
from .upload_file import MIMETYPES, File
from .utils import read_file


class Client:
    _session: ClientSession
    _authorization: Authorization

    def __init__(self, *, authorization: Optional[Authorization] = None):
        """Lets you create a client instance

        :authorization: an authorization object
        """

        self._authorization = authorization or Authorization()
        self._session = ClientSession()
        self._started = True

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, exception_type, exception_value, exception_traceback
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Closes the client"""

        if not self._started:
            raise ClientNotStarted()

        await self._session.close()

    async def upload_file(
        self, file_path: str, *, mimetype: Optional[str] = None
    ) -> File:
        """Lets you upload a file to the cloud

        :file_path: the path of the file you want to upload
        :mimetype: the mimetype of the file

        :returns: ciberedev.upload_file.File
        """

        if not self._authorization.file.token:
            raise NoAuthorizationGiven()

        if not os.path.exists(file_path):
            raise InvalidFilePath(file_path)
        elif not mimetype:
            ext = file_path.split(".")[-1]
            mimetype = MIMETYPES.get(ext)
            if mimetype is None:
                raise UnknownMimeType(ext)
        red = await read_file(file_path, "rb")

        buffer = io.BytesIO(red)  # type: ignore
        res = await self._session.post(
            "https://i.cibere.dev/upload",
            data={"data": buffer},
            headers={
                "token": self._authorization.file.token,
                "mime": mimetype,
            },
        )
        raw_data = await res.json()
        if raw_data["status_code"] == 200:
            file = File(data=raw_data)
            return file
        else:
            if raw_data["error"] == "Invalid 'token' given":
                raise InvalidAuthorizationGiven()
            else:
                raise UnknownError(raw_data["message"])

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

    async def create_embed(self, data: EmbedData) -> Embed:
        """Creates an embed

        :data: the embeds data

        :returns: ciberedev.embeds.Embed
        """

        data_keys = data.keys()
        if ("thumbnail" in data_keys) and ("image" in data_keys):
            raise TypeError("Thumbnail and Image Fields given")

        params = {}

        for param in data_keys:
            if param == "description":
                params["desc"] = data[param]  # type: ignore

            elif param not in EmbedFields:
                raise UnknownEmbedField(param)

            else:
                params[param] = data[param]
        params = urlencode(params)
        request = await self._session.post(
            f"https://www.cibere.dev/embed/upload?{params}", ssl=False
        )
        json = await request.json()
        embed = Embed(data=json)
        return embed

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
