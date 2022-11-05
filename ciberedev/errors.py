class BaseError(Exception):
    pass


class EmbedError(BaseError):
    pass


class UnknownEmbedField(EmbedError):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"Unknown Embed Field Given: {self.field}")
