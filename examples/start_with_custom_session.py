import asyncio

import aiohttp

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    async with aiohttp.ClientSession() as cs:
        # starting our client while passing a session arg
        await client.start(session=cs)

        # do stuff with the client here

        # we do not need to close the client
        # since all closing the client does is closing the clientsession
        # but since we gave our own client session, we can close it ourselves
        # and since we are using a context manager for our session
        # it will automatically close


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
