class BaseError(Exception):
    pass

class InvalidSessionError(BaseError):
    def __init__(self):
        super().__init__("Invalid Session Given")