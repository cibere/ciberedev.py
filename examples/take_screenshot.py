import asyncio

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    # starting our client with a context manager
    async with client:
        # taking our screenshot
        screnshot = await client.take_screenshot("www.google.com")
        # printing the screenshots url
        print(screnshot.url)

        # saving the screenshot to a file
        await screnshot.save("test.png")


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
