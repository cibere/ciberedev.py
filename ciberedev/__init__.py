"""
cibere.dev python wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper cibere.dev
"""

__description__ = "A basic wrapper cibere.dev"
__version__ = "0.4.0"

from typing import Literal, NamedTuple

from .client import Client
from .errors import *
from .screenshot import Screenshot
from .searching import SearchResult


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str


raw_version = __version__.split(".")
readable_releaselevel = {"a": "alpha", "b": "beta", "c": "candidate"}
version_info = VersionInfo(
    major=int(raw_version[0]),
    minor=int(raw_version[1]),
    micro=int(raw_version[2][0]),
    releaselevel=readable_releaselevel.get(raw_version[2][1], "final"),
)

del Literal, NamedTuple, VersionInfo, readable_releaselevel, raw_version
