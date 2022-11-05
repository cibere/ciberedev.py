<h1>ciberedev.py</h1>
<p>Python Wrapper for <a href="https://www.cibere.dev">cibere.dev</a></p>

<h2>Installing</h2>
<span style="font-weight: bold;">Python 3.8 or higher is required</span>
Install from pip
```
python -m pip install -U ciberedev.py
```
Install from github
```
python -m pip install -U https://github.com/cibere/ciberedev.py
```

<h2>Examples</h2>
Create Paste Example

```py
import asyncio

import ciberedev

client = ciberedev.Client()

async def main():
async with client:
embed = await client.create_paste("my_paste_text")
print(embed.url)

if **name** == "**main**":
asyncio.run(main())
```
