"""
cibere.dev python wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper cibere.dev (and discord oauth2)
"""

__description__ = "A basic wrapper cibere.dev (and discord oauth2)"
__version__ = "0.2.0"

from .authorization import Authorization, FileUploaderAuthorization
from .client import Client
