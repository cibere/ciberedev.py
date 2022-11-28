import asyncio

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    # starting our client with a context manager
    async with client:
        # getting our search results
        results = await client.get_search_results("cibere.dev")

        # printing the first results title, url, and description
        print(results[0].title)
        print(results[0].url)
        print(results[0].description)


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
