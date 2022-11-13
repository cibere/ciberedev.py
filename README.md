<h1 align="center">ciberedev.py</h1>
<p align="center">
<a href="https://discord.gg/pP4mKKbRvk"><img src="https://discord.com/api/guilds/986344051110473769/embed.png" alt="discord"></a>
<a href="https://pypi.org/project/ciberedev.py"><img src="https://img.shields.io/pypi/v/ciberedev.py.svg" alt="pypi"></a>
<a href="https://github.com/cibere/ciberedev.py/blob/main/LICENSE"><img src="https://img.shields.io/github/license/cibere/ciberedev.py" alt="license"></a>
</p>
<p align="center">Python Wrapper for <a href="https://www.cibere.dev">cibere.dev</a> (and discord oauth2)</p>

<h2>Key Features</h2>
Support for the following endpoints<br>
- screenshot<br>
- create paste<br>
- create embed<br>
- upload file<br>
- search the internet

<h2>Installing</h2>
<span style="font-weight: bold;">Python 3.8 or higher is required</span>
Install from pip

```
python -m pip install -U ciberedev.py
```

Install from github

```bash
python -m pip install -U git+https://github.com/cibere/ciberedev.py # requires git to be installed
```

<h2>Examples</h2>
Create Paste Example

```py
import asyncio

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    # starting our client with a context manager
    async with client:
        # creating our pasge
        paste = await client.create_paste("my_paste_text")
        # printing the pastes url
        print(paste.url)


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
```

See <a href="https://github.com/cibere/ciberedev.py/tree/main/examples">the examples folder</a> for a full list of examples
