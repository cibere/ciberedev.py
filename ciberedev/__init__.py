"""
cibere.dev python wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper cibere.dev
"""

__description__ = "A basic wrapper cibere.dev"
__version__ = "0.2.1"

from .authorization import Authorization, FileUploaderAuthorization
from .client import Client


def _get_version():
    VERSION = __version__
    if VERSION.startswith("BETA"):
        try:
            import subprocess

            p = subprocess.Popen(
                ["git", "rev-list", "--count", "HEAD"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out, err = p.communicate()
            if out:
                VERSION += out.decode("utf-8").strip()
            p = subprocess.Popen(
                ["git", "rev-parse", "--short", "HEAD"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out, err = p.communicate()
            if out:
                VERSION += "+g" + out.decode("utf-8").strip()
        except Exception:
            pass
    return VERSION
