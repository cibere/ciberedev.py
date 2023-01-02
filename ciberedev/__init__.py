"""
cibere.dev python wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper cibere.dev

.. include:: ../extras/index_page.md
.. include:: ../extras/update-log.md
"""

__description__ = "A basic wrapper cibere.dev"
__version__ = "0.4.3"

from typing import Literal, NamedTuple

from .client import Client
from .errors import *
from .file import File
from .searching import SearchResult


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str


raw_version = __version__.split(".")
try:
    raw_release_releaselevel = {"a": "alpha", "b": "beta", "c": "candidate"}.get(
        raw_version[2][1], "final"
    )
except IndexError:
    raw_release_releaselevel = "final"
version_info = VersionInfo(
    major=int(raw_version[0]),
    minor=int(raw_version[1]),
    micro=int(raw_version[2][0]),
    releaselevel=raw_release_releaselevel,
)

del Literal, NamedTuple, VersionInfo, raw_release_releaselevel, raw_version
