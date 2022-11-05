import setuptools

import ciberedev

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

with open("requirements.txt", "r") as f:
    REQUIREMENTS = f.read().splitlines()

setuptools.setup(
    name="ciberedev.py",
    version=ciberedev.__version__,
    author="cibere",
    author_email="cibere.dev@gmail.com",
    packages=["ciberedev"],
    description=ciberedev.__description__,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/cibere/cibere-dev.py",
    license="MIT",
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
)
