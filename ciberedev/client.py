from typing import Optional
from urllib.parse import urlencode

from aiohttp import ClientSession
from typing_extensions import Self

from .embeds import Embed, EmbedData, EmbedFields
from .errors import UnknownEmbedField
from .pasting import Paste


class Client:
    _session: ClientSession

    def __init__(self):
        pass

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

    async def create_embed(self, data: EmbedData) -> Embed:
        """Creates an embed

        :data: the embeds data
        """

        if ("thumbnail" in data.keys()) and ("image" in data.keys()):
            raise TypeError("Thumbnail and Image Fields given")

        params = {}

        for param in data.keys():
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
