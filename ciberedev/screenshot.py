from io import BytesIO

__all__ = ["Screenshot"]


class Screenshot:
    url: str
    bytes: BytesIO

    __slots__ = ["url", "bytes"]

    def __init__(self, *, _bytes: BytesIO, url: str):
        """Creates a Screenshot object.

        THIS SHOULD NOT BE CREATED MANUALLY, LET CIBEREDEV'S INTERNALS CREATE THEM

        Parameters
        ----------
        _bytes: io.BytesIO
            The image's bytes
        url: `str`
            The screenshots url

        Attributes
        ----------
        bytes: `io.BytesIO`
            The image's bytes
        url: str
            The screenshots url
        """

        self.url: str = url
        "the screenshots url"

        self.bytes: BytesIO = _bytes
        "the screenshots BytesIO object"
