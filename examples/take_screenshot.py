import asyncio

import ciberedev
from ciberedev.authorization import Authorization, ScreenshotAuthorization

# creating an authorization object
auth = Authorization(
    # adding our screenshot authorization
    screenshot=ScreenshotAuthorization(token="...")
)

# creating our client instance, and passing our authorization
client = ciberedev.Client(authorization=auth)


async def main():
    # starting our client with a context manager
    async with client:
        # taking our screenshot
        screnshot = await client.take_screenshot("www.google.com")
        # printing the screenshots url
        print(screnshot.url)


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
