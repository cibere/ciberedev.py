import io
import os
from typing import Optional
from urllib.parse import urlencode

import aiofiles
import validators
from aiohttp import ClientSession
from typing_extensions import Self

from .authorization import Authorization
from .discord_oauth import DiscordOauth
from .embeds import Embed, EmbedData, EmbedFields
from .errors import (
    InvalidAuthorizationGiven,
    InvalidFilePath,
    InvalidURL,
    NoAuthorizationGiven,
    UnableToConnect,
    UnknownEmbedField,
    UnknownError,
    UnknownMimeType,
)
from .pasting import Paste
from .screenshot import Screenshot
from .upload_file import MIMETYPES, File


class Client:
    _session: ClientSession
    _authorization: Authorization
    discord_oauth: DiscordOauth

    def __init__(self, *, authorization: Optional[Authorization] = None):
        """Lets you create a client instance

        :authorization: an authorization object
        """
        self._authorization = authorization or Authorization()

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self, exception_type, exception_value, exception_traceback
    ) -> None:
        await self.close()

    async def start(self, session: Optional[ClientSession] = None) -> None:
        """Starts the client

        :session: if you already have an aiohttp session that you would like to be used, you can pass it here
        """

        self._session = session or ClientSession()
        self.discord_oauth = DiscordOauth(
            auth=self._authorization, session=self._session
        )

    async def close(self) -> None:
        """Closes the client

        IF YOU PROVIDED A SESSION, THIS WILL CLOSE IT
        """

        await self._session.close()

    async def upload_file(
        self, file_path: str, *, mimetype: Optional[str] = None
    ) -> File:
        """Lets you upload a file to the cloud

        :file_path: the path of the file you want to upload
        :mimetype: the mimetype of the file"""
        if not self._authorization.file.token:  # type: ignore
            raise NoAuthorizationGiven()

        if not os.path.exists(file_path):
            raise InvalidFilePath(file_path)
        elif not mimetype:
            ext = file_path.split(".")[-1]
            mimetype = MIMETYPES.get(ext)
            if mimetype is None:
                raise UnknownMimeType(ext)
        async with aiofiles.open(file_path, "rb") as f:
            red = await f.read()

        buffer = io.BytesIO(red)
        res = await self._session.post(
            "https://i.cibere.dev/upload",
            data={"data": buffer},
            headers={
                "token": self._authorization.file.token,  # type: ignore
                "username": self._authorization.file.username,  # type: ignore
                "mime": mimetype,
            },
        )
        raw_data = await res.json()
        if raw_data["status_code"] == 200:
            file = File(data=raw_data)
            return file
        else:
            if raw_data["error"] in (
                "Invalid 'username' given",
                "Invalid 'token' given",
            ):
                raise InvalidAuthorizationGiven()
            else:
                raise UnknownError(raw_data["message"])

    async def take_screenshot(
        self, url: str, /, *, delay: Optional[int] = 0
    ) -> Screenshot:
        """Takes a screenshot of the given url

        :url: the url you want a screenshot of
        :delay: the delay between opening the link and taking the actual picture
        """

        if not self._authorization.screenshot.token:  # type: ignore
            raise NoAuthorizationGiven()

        url = url.removeprefix("<").removesuffix(">")

        if not url.startswith("http"):
            url = f"http://{url}"

        if not validators.url(url):  # type: ignore
            raise InvalidURL(url)

        raw_data = {"url": url, "delay": delay, "mode": "short"}
        data = urlencode(raw_data)
        headers = {"token": self._authorization.screenshot.token}  # type: ignore
        res = await self._session.post(
            f"https://api.cibere.dev/screenshot?{data}",
            headers=headers,
            verify_ssl=False,
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
            f"https://www.cibere.dev/embed/upload?{params}", verify_ssl=False
        )
        json = await request.json()
        embed = Embed(data=json)
        return embed

    async def create_paste(self, text: str) -> Paste:
        """Creates a paste

        :text: the text you want sent to the paste
        :session: if you already have an aiohttp session that you would like to be used, you can pass it here
        """

        data = {"text": text}

        request = await self._session.post(
            "https://paste.cibere.dev/upload", data=data, verify_ssl=False
        )
        json = await request.json()
        paste = Paste(data=json)
        return paste
