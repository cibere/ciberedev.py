from typing import Optional, TypedDict

from aiohttp import ClientSession


class RawPasteData(TypedDict):
    url: str
    code: str
    status_code: int
    message: str


class Paste:
    def __init__(self, *, data: RawPasteData):
        self.url = data.get("url")
        self.code = data.get("code")



async def create_paste(text: str, *, session: Optional[ClientSession] = None) -> Paste:
    """Creates a paste

    :text: the text you want sent to the paste
    :session: if you already have an aiohttp session that you would like to be used, you can pass it here
    """
    close_client = False
    if not session:
        session = ClientSession()
        close_client = True
    
    try:
        data = {"text": text}

        request = await session.post(
            "https://paste.cibere.dev/upload", data=data, verify_ssl=False
        )
        json = await request.json()
        paste = Paste(data=json)
        return paste
    
    except Exception as e:
        raise e
    
    finally:
        if close_client:
            await session.close()