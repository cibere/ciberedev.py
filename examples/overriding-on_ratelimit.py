import asyncio

import ciberedev


# subclassing ciberedev.Client so its easier to override, though
# client = ciberedev.Client()
# client.on_ratelimit = ...
# still works as well
class Client(ciberedev.Client):
    # here we actually override it
    async def on_ratelimit(self, endpoint: str) -> None:
        # endpoint is the endpoint the ratelimit is coming from. Ex: `/screenshot`
        print("WE ARE BEING RATELIMITED, STOP MAKING STUPID API REQUESTS")

        # if you still want the library to send logs to the console, you can call the super on_ratelimit
        await super().on_ratelimit(endpoint)


# creating an instance of our newly subclassed client
client = Client()


async def main():
    # starting our client with a context manager
    async with client:
        # do stuff with the client here
        pass


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
