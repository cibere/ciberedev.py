import asyncio
from functools import partial


async def read_file(filename: str, mode: str) -> str:
    """Reads the given file"""

    def sync_func(fn: str, mode: str):
        with open(fn, mode=mode) as f:
            txt = f.read()
            return txt

    func = partial(sync_func, filename, mode)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func)