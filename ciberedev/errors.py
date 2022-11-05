class BaseError(Exception):
    pass


class UnknownError(BaseError):
    def __init__(self, error: str):
        self.error = error
        super().__init__(f"An unknown error has occured: {error}")


class AuthorizationError(BaseError):
    pass


class NoAuthorizationGiven(AuthorizationError):
    def __init__(self):
        super().__init__("No Authorization Passed When Creating Client Instance")


class InvalidAuthorizationGiven(AuthorizationError):
    def __init__(self):
        super().__init__("Invalid Authorization Given")


class EmbedError(BaseError):
    pass


class UnknownEmbedField(EmbedError):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"Unknown Embed Field Given: '{self.field}'")


class ScreenshotError(BaseError):
    pass


class InvalidURL(ScreenshotError):
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Invalid URL Given: '{self.url}'")


class UnableToConnect(ScreenshotError):
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Unable to Connect to '{self.url}'")
