from typing import Optional
from urllib.parse import urlencode

import validators
from aiohttp import ClientSession
from typing_extensions import Self

from .embeds import Embed, EmbedData, EmbedFields
from .errors import (
    InvalidAuthorizationGiven,
    InvalidURL,
    NoAuthorizationGiven,
    UnableToConnect,
    UnknownEmbedField,
    UnknownError,
)
from .pasting import Paste
from .screenshot import Screenshot


class Client:
    _session: ClientSession
    _token: str

    def __init__(self, *, token: Optional[str] = None):
        self._token = token or ""

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

    async def close(self) -> None:
        """Closes the client

        IF YOU PROVIDED A SESSION, THIS WILL CLOSE IT
        """

        await self._session.close()

    async def take_screenshot(
        self, url: str, /, *, delay: Optional[int] = 0
    ) -> Screenshot:
        """Takes a screenshot of the given url

        :url: the url you want a screenshot of
        :delay: the delay between opening the link and taking the actual picture
        """

        if not self._token:
            raise NoAuthorizationGiven()

        url = url.removeprefix("<").removesuffix(">")

        if not url.startswith("http"):
            url = f"http://{url}"

        if not validators.url(url):  # type: ignore
            raise InvalidURL(url)

        raw_data = {"url": url, "delay": delay, "mode": "short"}
        data = urlencode(raw_data)
        headers = {"token": self._token}
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