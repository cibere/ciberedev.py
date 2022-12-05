__all__ = [
    "ClientNotStarted",
    "UnknownError",
    "InvalidURL",
    "UnableToConnect",
    "APIOffline",
    "InvalidPattern",
    "UnableToDemote",
    "UnableToPromote",
    "LocationAlreadyTaken",
]


class CiberedevException(Exception):
    pass


class APIException(CiberedevException):
    pass


class ScreenshotException(CiberedevException):
    pass


class BoardgameException(CiberedevException):
    pass


class CheckersException(BoardgameException):
    pass


class APIOffline(APIException):
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


class ClientNotStarted(APIException):
    def __init__(self):
        """Creates a ClientNotStarted error instance.

        It is not recommended to raise this yourself
        """

        super().__init__(
            "Client has not been started. You can start it with 'client.run' or 'client.start'"
        )


class UnknownError(CiberedevException):
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


class InvalidURL(ScreenshotException):
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


class UnableToConnect(ScreenshotException):
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


class LocationAlreadyTaken(CheckersException):
    def __init__(self, location: int):
        """Creates a LocationAlreadyTaken error instance

        It is not recommended to raise this yourself

        Parameters
        ----------
        loaction: int
            the location you are trying to move a piece to

        Attributes
        ----------
        loaction: int
            the location you are trying to move a piece to
        """

        self.location = location
        super().__init__(f"There is already a piece at '{location}'")


class UnableToPromote(CheckersException):
    def __init__(self):
        """Creates a UnableToPromote error instance

        It is not recommended to raise this yourself
        """

        super().__init__("This piece can not be promoted anymore")


class UnableToDemote(CheckersException):
    def __init__(self):
        """Creates a UnableToDemote error instance

        It is not recommended to raise this yourself
        """

        super().__init__("This piece can not be demoted anymore")


class InvalidPattern(CheckersException):
    def __init__(self, error: str, pattern: str):
        """Creates a InvalidPattern error instance

        It is not recommended to raise this yourself

        Parameters
        ----------
        pattern: `str`
            the invalid pattern
        error: `str`
            How the pattern is invalid

        Attributes
        ----------
        pattern: `str`
            the invalid pattern
        """

        self.pattern = pattern
        super().__init__(error)
