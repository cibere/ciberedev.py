import asyncio

import ciberedev

# creating our client instance
client = ciberedev.Client()


async def main():
    # starting our client with a context manager
    async with client:
        # creating a checkers game instance
        # not passing a pattern gives you the default layout of when you start a game
        game = await client.create_checkers_game()

        # generating a board file
        board = await game.generate_board()
        # saving the file
        await board.save("before_board.png")

        # getting the piece we want to move
        piece = await game.get_piece_at(0)
        # actually moving the piece.
        # keep in mind that `piece` *could* be `None`
        # Though in this example we know its not, since we are creating a fresh game, so `0` will always be a black piece
        piece.move(8)

        # generating the board again, and saving it.
        board = await game.generate_board()
        await board.save("after_board.png")


# checking if this file is the one that was run
if __name__ == "__main__":
    # if so, run the main function
    asyncio.run(main())
