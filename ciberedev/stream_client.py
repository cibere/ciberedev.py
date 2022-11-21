import asyncio
import json
from typing import Optional

import aiohttp
from aiohttp import ClientSession
from typing_extensions import Self

from .authorization import Authorization
from .errors import ClientAlreadyStarted, ClientNotStarted, InvalidAuthorizationGiven

_supported_logs = {
    "update embed": "embed_update",
    "upload file": "file_upload",
    "change password": "password_change",
    "change token": "token_reset",
}


class StreamClient:
    _session: ClientSession
    _authorization: Authorization

    def __init__(self, *, authorization: Authorization):
        """Lets you create a client instance

        :authorization: an authorization object
        """

        self._authorization = authorization or Authorization()
        self._started = False

    async def __aenter__(self) -> Self:
        if self._started:
            raise ClientAlreadyStarted()

        self._session = ClientSession()
        self._started = True
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

    async def start(self) -> None:
        """Starts the client"""

        if not self._started:
            async with ClientSession() as session:
                self._session = session
                self._started = True
                await self._start()
        else:
            await self._start()

    async def _start(self) -> None:
        while self._started:
            async with self._session.ws_connect("https://i.cibere.dev/websocket") as ws:
                await ws.send_json(
                    {
                        "request": "get_new_logs",
                        "authorization": self._authorization.file.token,
                    }
                )
                async for msg in ws:
                    data = json.loads(msg.data)

                    if data.get("error") == "Invalid Authorization":
                        raise InvalidAuthorizationGiven()

                    if data["message"] != "you have no new logs":
                        event = str(_supported_logs.get(data["data"]["action"]))
                        await self.dispatch(
                            event, data["data"]["link"], data["data"]["timestamp"]
                        )

                    await asyncio.sleep(1)
                    await ws.send_json(
                        {
                            "request": "get_new_logs",
                            "authorization": self._authorization.file.token,
                        }
                    )
                    if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        break

    async def dispatch(self, event_name: str, *args):
        if hasattr(self, f"on_{event_name}"):
            event = getattr(self, f"on_{event_name}")
            await event(*args)

    async def on_file_upload(self, link: str, timestamp: str) -> None:
        pass

    async def on_embed_update(self) -> None:
        pass

    async def on_password_change(self) -> None:
        pass

    async def on_token_reset(self) -> None:
        pass

    def event(self, coro):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event must be a coroutine")

        setattr(self, coro.__name__, coro)
        return coro
