import aiohttp
from typing import TypedDict
from .errors import InvalidSessionError

class RawPasteData(TypedDict):
    url: str
    code: str
    status_code: int
    message: str

class Paste:
    def __init__(self, *, data: RawPasteData):
        self.url = data.get("url")
        self.code = data.get("code")

async def create_paste(text: str, *, session: aiohttp.ClientSession = None) -> Paste:
    """Creates a paste
    
    :text: the text you want sent to the paste
    
    :session: if you already have an aiohttp session that you would like to be used, you can pass it here
    """
    
    async def _create_paste(session_to_use: aiohttp.ClientSession):
        res = await session_to_use.post("https://paste.cibere.dev/upload", data={'text' : text}, verify_ssl=False)
        raw_data = await res.json()
        paste = Paste(data=raw_data)
        return paste
    
    if session:
        try:
            return await _create_paste(session)
        except:
            raise InvalidSessionError()
    else:
        async with aiohttp.ClientSession() as cs:
            return await _create_paste(cs)