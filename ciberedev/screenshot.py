from io import BytesIO

__all__ = ["Screenshot"]


class Screenshot:
    def __init__(self, *, _bytes: BytesIO, url: str):
        self._url: str = url
        self._bytes: BytesIO = _bytes

    @property
    def url(self) -> str:
        """the screenshots url"""

        return self._url

    @property
    def bytes(self) -> BytesIO:
        """the screenshots BytesIO object"""

        return self._bytes
