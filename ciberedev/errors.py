__all__ = [
    "ClientAlreadyClosed",
    "UnknownError",
    "InvalidURL",
    "UnableToConnect",
    "APIOffline",
    "UnknownDataReturned",
    "APIException",
    "UnknownStatusCode",
    "UnableToConvertToImage",
]


class CiberedevException(Exception):
    pass


class APIException(CiberedevException):
    def __init__(self, error: str):
        """Creates an APIException error stinace

        This is raised when the api returns an error
        It is not recommended to raise this yourself

        """

        super().__init__(error)


class UnknownStatusCode(APIException):
    def __init__(self, code: int):
        """Creates an UnknownStatusCode error stinace

        This is raised when the api returns an unknown status code
        It is not recommended to raise this yourself

        Parameters
        ----------
        code: `int`
            the status code that was returned

        Attributes
        ----------
        code: `int`
            the status code that was returned
        """

        self.code = code
        super().__init__(f"API returned an unknown status code: '{self.code}'")


class UnknownDataReturned(APIException):
    def __init__(self, endpoint: str):
        """Creates an UnknownDataReturned error stinace

        This is raised when the data the api returns does not match what the client believes it should return
        It is not recommended to raise this yourself

        Parameters
        ----------
        endpoint: `str`
            The endpoint the client is making a request to when this happend

        Attributes
        ----------
        endpoint: `str`
            The endpoint the client is making a request to when this happend
        """

        self.endpoint = endpoint
        super().__init__(
            f"API returned unknown data when making a request to '{endpoint}'"
        )


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


class ClientAlreadyClosed(APIException):
    def __init__(self):
        """Creates a ClientAlreadyClosed error instance.

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


class InvalidURL(CiberedevException):
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


class UnableToConnect(CiberedevException):
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


class UnableToConvertToImage(CiberedevException):
    def __init__(self, url: str):
        """Creates a UnableToConvertToImage error instance.

        It is not recommended to raise this yourself

        Parameters
        ----------
        url: `str`
            The url that the API is unable to convert into an image

        Attributes
        ----------
        url: `str`
            The url that the API is unable to convert into an image
        """

        self.url = url
        super().__init__(f"The API is unable to convert '{self.url}' into an image")
