import asyncio

import ciberedev
from ciberedev.authorization import Authorization, DiscordOauthAuthorization

# creating our authorization object
auth = Authorization(
    discord_oauth=DiscordOauthAuthorization(
        client_id=123,
        client_secret="...",
        redirect_url="https://api.cibere.dev/discord_oauth",
        discord_api_version=10,
    )
)

# creating our client instance and passing our authorization
client = ciberedev.Client(authorization=auth)


async def main():
    # starting our client
    async with client:
        # exchanging our code with discord for our original token
        old_token = await client.discord_oauth.exchange_code("...")

        # refreshing our token with discord for a new token
        new_token = await client.discord_oauth.refresh_token(old_token.refresh_token)

        # printing our new token
        print(new_token.token)


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
