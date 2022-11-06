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
        # exchanging our code with discord for a token
        token = await client.discord_oauth.exchange_code("...")

        # getting the users info
        user = await client.discord_oauth.get_user_info(
            token.token
        )  # 'token' is a ciberedev.discord_oauth.Token object

        # printing the users nmae
        print(user.name)


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
