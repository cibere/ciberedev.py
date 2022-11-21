"""
cibere.dev python wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper cibere.dev
"""

__description__ = "A basic wrapper cibere.dev"
__version__ = "0.2.1"

from .authorization import Authorization, FileUploaderAuthorization
from .client import Client
from .stream_client import StreamClient