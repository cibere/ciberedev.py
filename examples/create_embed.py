import asyncio

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    # starting our client with a context manager
    async with client:
        # creating our embeds data
        data = {
            "title": "My Embeds Title",
            "description": "My Embeds Description",
            "author": "my embeds author",
        }
        # creating our actual embed
        embed = await client.create_embed(data)
        # printing the embeds url
        print(embed.url)


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
