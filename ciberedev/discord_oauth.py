from typing import Union

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

    def __str__(self):
        return self.name


class Email:
    def __init__(self, *, verified: bool, email: str):
        self.verified: bool = verified
        self.email: str = email

    def __str__(self):
        return self.email


class Flags:
    def __init__(self, *, flag_value: int):
        pass


class Token:
    def __init__(self, *, raw_data: dict):
        self.token: str = raw_data["access_token"]
        self.refresh_token: str = raw_data["refresh_token"]
        self.expires: int = raw_data["expires_in"]
        self.scopes: list[str] = raw_data["scope"].split(" ")

    def __str__(self):
        return self.token


class PartialUser:
    def __init__(self, *, raw_data: dict):
        self.id: int = int(raw_data["id"])
        self.name: str = raw_data["username"]
        self.discriminator: int = int(raw_data["discriminator"])
        self.locale: Union[str, None] = raw_data.get("locale")

        self.bot: bool = bool(raw_data.get("bot", False))
        self.system: bool = bool(raw_data.get("system", False))
        self.mfa_enabled: bool = bool(raw_data.get("mfa_enabled", False))

        self._banner_id: str = raw_data.get("banner", None)
        self._accent_color: Union[int, None] = raw_data.get("accent_color")
        self._email_verified: Union[bool, None] = raw_data.get("verified")
        self._email: Union[str, None] = raw_data.get("email")
        if self._email:
            self.email = Email(verified=self._email_verified, email=self.email)  # type: ignore
        else:
            self.email = None

        self._flags: Union[int, None] = raw_data.get("flags")
        self._premium_type: Union[int, None] = raw_data.get("premium_type")
        self._public_flags: Union[int, None] = raw_data.get("public_flags")

    @property
    def banner_url(self):
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self._banner_id}.png"

    @property
    def accent_color(self):
        if self._accent_color:
            return int(self._accent_color)
        else:
            return None

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

    async def refresh_token(self, refresh_token: str) -> Token:
        """refreshes an oauth2 token

        :refresh_token: the refresh_token for the old token
        """
        if not self._authorization.discord_oauth.was_given:  # type: ignore
            raise NoAuthorizationGiven()

        data = {
            "client_id": str(self._authorization.discord_oauth.client_id),  # type: ignore
            "client_secret": self._authorization.discord_oauth.client_secret,  # type: ignore
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": self._authorization.discord_oauth.redirect_url,  # type: ignore
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        res = await self._session.post(
            self._authorization.discord_oauth.api_endpoint + "/oauth2/token", data=data, headers=headers  # type: ignore
        )
        try:
            raw_data = await res.json()
            token = raw_data["access_token"]  # type: ignore
        except KeyError:
            raise InvalidTokenGiven(refresh_token)

        token = Token(raw_data=raw_data)
        return token

    async def exchange_code(self, code: str) -> Token:
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
            raw_data = await res.json()
            token = raw_data["access_token"]
        except KeyError:
            raise InvalidCodeGiven(code)

        token = Token(raw_data=raw_data)
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
