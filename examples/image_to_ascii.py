import asyncio

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    # starting our client with a context manager
    async with client:

        # converting out image to ascii
        result = await client.convert_image_to_ascii("https://i.cibere.dev/1cgix6.png")

        # printing our ascii art
        print(result)


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
