import asyncio

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    # starting our client without a context manager
    await client.start()

    # do stuff with the client here

    # closing/stopping the client
    await client.close()


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
