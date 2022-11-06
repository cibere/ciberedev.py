from typing import Optional


class FileUploaderAuthorization:
    def __init__(self, *, username: Optional[str] = None, token: Optional[str] = None):
        self.username = username
        self.token = token


class ScreenshotAuthorization:
    def __init__(self, *, token: Optional[str] = None):
        self.token = token


class DiscordOauthAuthorization:
    def __init__(
        self,
        *,
        client_id: Optional[int] = None,
        client_secret: Optional[str] = None,
        redirect_url: Optional[str] = None,
        discord_api_version: Optional[int] = 10,
    ):
        self.api_endpoint = f"https://discord.com/api/v{discord_api_version}"
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url

    @property
    def was_given(self) -> bool:
        return (
            self.client_id is None
            and self.client_secret is None
            and self.redirect_url is None
        )


class Authorization:
    def __init__(
        self,
        *,
        screenshot: Optional[ScreenshotAuthorization] = ScreenshotAuthorization(),
        file_uploader: Optional[
            FileUploaderAuthorization
        ] = FileUploaderAuthorization(),
        discord_oauth: Optional[
            DiscordOauthAuthorization
        ] = DiscordOauthAuthorization(),
    ):
        self.screenshot = screenshot
        self.file = file_uploader
        self.discord_oauth = discord_oauth
