import asyncio

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    # starting our client with a context manager
    async with client:
        # here we define our pattern.
        # a pattern should be 32 characters long
        # r = normal red piece
        # b = normal black piece
        # q = black queen piece
        # k = red queen piece
        pattern = "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"

        # creating a checkers game instance
        # and passing our pattern in
        game = await client.create_checkers_game(pattern=pattern)

        # generating a board file
        board = await game.generate_board()
        # saving the file
        await board.save("generated_board.png")


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
