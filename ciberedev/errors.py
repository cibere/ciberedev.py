__all__ = ["ClientNotStarted", "UnknownError", "InvalidURL", "UnableToConnect"]


class BaseError(Exception):
    pass


class ClientNotStarted(BaseError):
    def __init__(self):
        super().__init__(
            "Client has not been started. You can start it with 'client.run' or 'client.start'"
        )


class ClientAlreadyStarted(BaseError):
    def __init__(self):
        super().__init__("Client has already been started")


class UnknownError(BaseError):
    def __init__(self, error: str):
        self.error = error
        super().__init__(f"An unknown error has occured: {error}")


class ScreenshotError(BaseError):
    pass


class InvalidURL(ScreenshotError):
    def __init__(self, url: str):
        self._url: str = url
        super().__init__(f"Invalid URL Given: '{self.url}'")

    @property
    def url(self) -> str:
        """the url that has been marked as invalid"""

        return self._url


class UnableToConnect(ScreenshotError):
    def __init__(self, url: str):
        self._url: str = url
        super().__init__(f"Unable to Connect to '{self.url}'")

    @property
    def url(self) -> str:
        """The url that the API is unable to connect to"""

        return self._url
