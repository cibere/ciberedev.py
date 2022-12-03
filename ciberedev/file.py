import asyncio
from functools import partial as partial_func
from typing import Any, Optional, Union

__all__ = ["File"]


def _write_to_file(filepath: str, data: Any) -> None:
    with open(filepath, "wb") as f:
        f.write(data)


class File:
    def __init__(self, *, raw_bytes: bytes, url: Optional[str] = None):
        """Creates a file object

        Parameters
        ----------
        raw_bytes: `bytes`
            The bytes of the file
        url: Optional[`url`]
            the files url (if it has one)

        Parameters
        ----------
        raw_bytes: `bytes`
            The bytes of the file
        url: Optional[`url`]
            the files url (if it has one)
        """

        self.bytes = raw_bytes
        self.url = url

    async def save(self, fp: str, /) -> None:
        """Saves the file

        Paramters
        ----------
        fp: `str`
            The filepath/filename the file should be saved to
        """

        func = partial_func(_write_to_file, fp, self.bytes)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, func)
