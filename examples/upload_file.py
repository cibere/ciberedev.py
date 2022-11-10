import asyncio

import ciberedev
from ciberedev.authorization import Authorization, FileUploaderAuthorization

# creating an authorization object
auth = Authorization(
    # adding our file uploader authorization
    file_uploader=FileUploaderAuthorization(token="...")
)

# creating our client instance, and passing our authorization
client = ciberedev.Client(authorization=auth)


async def main():
    # starting our client with a context manager
    async with client:
        # uploading our file
        file = await client.upload_file("n5TevB.png")
        # printing our files link
        print(file.url)


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
