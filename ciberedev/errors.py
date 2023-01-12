__all__ = [
    "ClientAlreadyClosed",
    "APIOffline",
    "UnknownDataReturned",
    "HTTPException",
    "UnknownStatusCode",
    "InternalServerError",
]


class CiberedevException(Exception):
    pass


class HTTPException(CiberedevException):
    def __init__(self, error: str):
        """Creates an APIException error stinace

        This is raised when the api returns an error
        It is not recommended to raise this yourself

        """

        super().__init__(error)


class UnknownStatusCode(HTTPException):
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


class UnknownDataReturned(HTTPException):
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


class APIOffline(HTTPException):
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


class ClientAlreadyClosed(CiberedevException):
    def __init__(self):
        """Creates a ClientAlreadyClosed error instance.

        It is not recommended to raise this yourself
        """

        super().__init__(
            "Client has not been started. You can start it with 'client.run' or 'client.start'"
        )


class InternalServerError(CiberedevException):
    def __init__(self):
        """Creates a InternalServerError error instance

        It is not recommended to raise this yourself"""
        super().__init__("We have run out of attempts, aborting request")
