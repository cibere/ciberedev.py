from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, Literal, Optional, Union

from typing_extensions import Self

if TYPE_CHECKING:
    from .http import HTTPClient


class PlayingPiece:
    def __init__(
        self,
        *,
        _type: Literal["black", "red", "black queen", "red queen"],
        location: int,
        board: CheckersGame,
    ):
        self.type = _type
        self.raw = {"black": "b", "red": "r", "black queen": "q", "red queen": "k"}[
            self.type
        ]
        self._location = location
        self._board = board

    def __str__(self):
        return self.type

    def __repr__(self):
        return f"<PlayingPiece type='{self.type}' location: '{self._location}'"

    @property
    def location(self) -> int:
        return self._location

    @location.setter
    def location(self, new_location: int):
        if not isinstance(new_location, int):
            raise TypeError("The location must be an integer")

        self.move(new_location)

    def move(self, new_location: int, /):
        if new_location < 0 or new_location > 32:
            raise TypeError("The location must be inbetween 0 and 32")
        if not isinstance(self._board.pieces[new_location], EmptySpace):
            raise TypeError("There is already a piece at the given location")

        self._board.pieces[self._location] = EmptySpace()
        self._board.pieces[new_location] = self
        self._location = new_location


class EmptySpace:
    raw = "_"


class CheckersGame:
    __slots__ = ["_http", "pieces"]

    def __init__(self, *, http_client: HTTPClient):
        self.pieces: list[Union[PlayingPiece, EmptySpace]] = []
        self._http = http_client

        for i in range(8):
            self.pieces.append(PlayingPiece(_type="black", location=i, board=self))
        for i in range(16):
            self.pieces.append(EmptySpace())
        for i in range(8):
            self.pieces.append(PlayingPiece(_type="red", location=i, board=self))

    async def get_piece_at(self, index: int) -> Optional[PlayingPiece]:
        piece = self.pieces[index]
        if isinstance(piece, EmptySpace):
            return None
        else:
            return piece

    @classmethod
    def from_pattern(cls, *, pattern: str, http_client: HTTPClient) -> Self:
        if len(pattern) != 32:
            raise TypeError("Pattern must be 32 characters long")
        if not all(char in ["b", "_", "r", "q", "k"] for char in pattern):
            raise TypeError("Invalid Character in pattern")

        self = cls.__new__(cls)

        pieces = []
        for index, char in enumerate(pattern):
            if char == "_":
                piece = EmptySpace()
            else:
                char_convertor = {
                    "q": "black queen",
                    "k": "red queen",
                    "b": "black",
                    "r": "red",
                }
                piece = PlayingPiece(
                    _type=char_convertor[char],  # type: ignore
                    location=index,
                    board=self,
                )
            pieces.append(piece)

        self._http = http_client
        self.pieces = pieces

        return self

    async def to_pattern(self) -> str:
        return "".join(piece.raw for piece in self.pieces)

    async def generate_board(self) -> bytes:
        pattern = await self.to_pattern()
        return await self._http.get_checkers_board(pattern)
