import asyncio

import ciberedev

auth = ciberedev.Authorization(
    file_uploader=ciberedev.FileUploaderAuthorization(token="...")
)

# creating our StreamClient instance and passing our authorization
client = ciberedev.StreamClient(authorization=auth)

# creating an event that will be triggered when a file is uploaded
@client.event
async def on_file_upload(link: str, timestamp: str):
    print("File uploaded")
    print(f"{link=}")
    print(f"{timestamp=}")


async def main():
    await client.start()


if __name__ == "__main__":
    asyncio.run(main())
