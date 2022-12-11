import asyncio

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    # starting our client with a context manager
    async with client:

        # getting 5 random words
        words = await client._http.get_random_words(5)

        # printing our random words
        print("\n".join(words))


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
