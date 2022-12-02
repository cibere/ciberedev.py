__all__ = [
    "ClientNotStarted",
    "UnknownError",
    "InvalidURL",
    "UnableToConnect",
    "APIOffline",
]


class BaseError(Exception):
    pass


class APIError(BaseError):
    pass


class APIOffline(APIError):
    def __init__(self, endpoint: str):
        """Creates an APIOffline error instance.

        This is raised when the client can not connect to the api
        It is not recommended to raise this yourself

        Parameters
        ----------
        endpoint: `str`
            the endpoint the client is trying to make a request to

        Attributes
        ----------
        endpoint: `str`
            the endpoint the client is trying to make a request to
        """

        self.endpoint = endpoint
        super().__init__(f"API is down. Aborting API request to '{endpoint}'")


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

        Parameters
        ----------
        error: `str`
            The unknown error that occured

        Attributes
        ----------
        error: `str`
            The unknown error that occured
        """

        self.error = error
        super().__init__(f"An unknown error has occured: {error}")


class ScreenshotError(BaseError):
    pass


class InvalidURL(ScreenshotError):
    def __init__(self, url: str):
        """Creates a InvalidURL error instance.

        It is not recommended to raise this yourself

        Parameters
        ----------
        url: `str`
            the url that is invalid

        Attributes
        ----------
        url: `str`
            the url that is invalid
        """

        self.url: str = url
        super().__init__(f"Invalid URL Given: '{self.url}'")


class UnableToConnect(ScreenshotError):
    def __init__(self, url: str):
        """Creates a UnableToConnect error instance.

        It is not recommended to raise this yourself

        Parameters
        ----------
        url: `str`
            The url that the API is unable to connect to

        Attributes
        ----------
        url: `str`
            The url that the API is unable to connect to
        """

        self.url: str = url
        super().__init__(f"Unable to Connect to '{self.url}'")
