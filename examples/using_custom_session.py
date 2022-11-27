import asyncio

from aiohttp import ClientSession

import ciberedev

# creating our custom session
session = ClientSession()

# creating our client instance, and passing a custom session
client = ciberedev.Client(session=session)


async def main():
    # do stuff with client here.

    # Because we are using a custom session, using a context manager or calling client.close will close our custom session.
    # but we need to remember to close our session manually
    await session.close()


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
