__all__ = ["ClientNotStarted", "UnknownError", "InvalidURL", "UnableToConnect"]


class BaseError(Exception):
    pass


class ClientNotStarted(BaseError):
    def __init__(self):
        """Creates a ClientNotStarted error instance.

        It is not recommended to raise this yourself
        """

        super().__init__(
            "Client has not been started. You can start it with 'client.run' or 'client.start'"
        )


class ClientAlreadyStarted(BaseError):
    def __init__(self):
        """Creates a ClientAlreadyStarted error instance.

        It is not recommended to raise this yourself
        """

        super().__init__("Client has already been started")


class UnknownError(BaseError):
    def __init__(self, error: str):
        """Creates a UnknownError error instance.

        It is not recommended to raise this yourself

        :error: The unknown error
        """

        self.error = error
        super().__init__(f"An unknown error has occured: {error}")


class ScreenshotError(BaseError):
    pass


class InvalidURL(ScreenshotError):
    def __init__(self, url: str):
        """Creates a InvalidURL error instance.

        It is not recommended to raise this yourself

        :url: the url that is invalid
        """

        super().__init__(f"Invalid URL Given: '{self.url}'")

        self.url: str = url
        "the url that has been marked as invalid"


class UnableToConnect(ScreenshotError):
    def __init__(self, url: str):
        """Creates a UnableToConnect error instance.

        It is not recommended to raise this yourself

        :url: the url that the api is unable to connect to
        """

        super().__init__(f"Unable to Connect to '{self.url}'")

        self.url: str = url
        "The url that the API is unable to connect to"
