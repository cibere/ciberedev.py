from aiohttp import ClientSession

from .authorization import Authorization
from .errors import InvalidCodeGiven, InvalidTokenGiven, NoAuthorizationGiven


class Connections:
    def __init__(self, *, raw_data: dict):
        self.id: int = raw_data["id"]
        self.name: str = raw_data["name"]
        self.type: str = raw_data["type"]
        self.verified: bool = bool(raw_data["verified"])
        self.friend_sync: bool = bool(raw_data["friend_sync"])
        self.show_activity: bool = bool(raw_data["show_activity"])
        self.two_way_link: bool = bool(raw_data["two_way_link"])
        self._visibility: bool = bool(raw_data["visibility"])

    @property
    def visible(self) -> bool:
        """returns true if its visible to everyone
        returns false if its invisible to everyone except the user themselves
        """
        return bool(self._visibility)


class PartialGuild:
    def __init__(self, *, raw_data: dict):
        self.id: int = raw_data["id"]
        self.name: str = raw_data["name"]
        self.permissions: int = raw_data["permissions"]
        self.features: list[str] = raw_data["features"]


class PartialUser:
    def __init__(self, *, raw_data: dict):
        self.id: int = int(raw_data["id"])
        self.name: str = raw_data["username"]
        self.discriminator: int = int(raw_data["discriminator"])

        self.bot: bool = bool(raw_data.get("bot", False))
        self.system: bool = bool(raw_data.get("system", False))
        self.mfa_enabled: bool = bool(raw_data.get("mfa_enabled", False))

    @property
    def username(self):
        return self.name

    def __str__(self):
        return f"{self.name}#{self.discriminator}"


class DiscordOauth:
    _session: ClientSession
    _authorization: Authorization

    def __init__(self, *, auth: Authorization, session: ClientSession):
        self._session = session
        self._authorization = auth

    async def refresh_token(self, token: str) -> str:
        """refreshes an oauth2 token

        :token: the old token
        """
        if not self._authorization.discord_oauth.was_given:  # type: ignore
            raise NoAuthorizationGiven()

        data = {
            "client_id": str(self._authorization.discord_oauth.client_id),  # type: ignore
            "client_secret": self._authorization.discord_oauth.client_secret,  # type: ignore
            "grant_type": "refresh_token",
            "refresh_token": token,
            "redirect_uri": self._authorization.discord_oauth.redirect_url,  # type: ignore
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        res = await self._session.post(
            self._authorization.discord_oauth.api_endpoint + "/oauth2/token", data=data, headers=headers  # type: ignore
        )
        try:
            token = await res.json()
            print(f"PAYLOAD RECIEVED: {token}")
            token = token["access_token"]  # type: ignore
        except KeyError:
            raise InvalidTokenGiven(token)

        return token

    async def exchange_code(self, code: str) -> str:
        """Exchanges an oauth2 code for a token

        :code: the code you got from oauth2
        """
        if not self._authorization.discord_oauth.was_given:  # type: ignore
            raise NoAuthorizationGiven()

        data = {
            "client_id": str(self._authorization.discord_oauth.client_id),  # type: ignore
            "client_secret": self._authorization.discord_oauth.client_secret,  # type: ignore
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._authorization.discord_oauth.redirect_url,  # type: ignore
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        res = await self._session.post(
            self._authorization.discord_oauth.api_endpoint + "/oauth2/token", data=data, headers=headers  # type: ignore
        )
        try:
            token = await res.json()
            print(f"PAYLOAD RECIEVED: {token}")
            token = token["access_token"]
        except KeyError:
            raise InvalidCodeGiven(code)

        return token

    async def get_user_connections(self, token: str) -> list[Connections]:
        """Get a users connections

        :token: the token you got from exchanging the oauth2 code
        """
        res = await self._session.get(
            "https://discord.com/api/v10/users/@me/connections",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = await res.json()
        print(f"PAYLOAD RECIEVED: {data}")
        cons = []
        for con in data:
            cons.append(Connections(raw_data=con))
        return cons

    async def get_user_guilds(self, token: str) -> list[PartialGuild]:
        """Get a users guilds

        :token: the token you got from exchanging the oauth2 code
        """
        res = await self._session.get(
            "https://discord.com/api/v10/users/@me/guilds",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = await res.json()
        print(f"PAYLOAD RECIEVED: {data}")
        guilds = []
        for guild in data:
            guilds.append(PartialGuild(raw_data=guild))
        return guilds

    async def get_user_info(self, token: str) -> PartialUser:
        """Get a users info

        :token: the token you got from exchanging the oauth2 code
        """
        res = await self._session.get(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = await res.json()
        user = PartialUser(raw_data=data)
        return user
