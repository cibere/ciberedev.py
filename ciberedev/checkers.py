from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Union

from typing_extensions import Self

from .errors import LocationAlreadyTaken, UnableToDemote, UnableToPromote
from .file import File

if TYPE_CHECKING:
    from .http import HTTPClient


class PlayingPiece:
    _raw_conversion = {"black": "b", "red": "r"}

    def __init__(
        self,
        *,
        _type: Literal["black", "red"],
        location: int,
        board: CheckersGame,
    ):
        """Creates a playing piece object

        Parameters
        ----------
        _type: `str`
            The type of piece it should be. `black`/`red`
        location: `int`
            where it should be put on the board
        board: `ciberedev.checkers.CheckersGame`
            the board it should be apart of
        """

        self.type = _type
        self.raw = self._raw_conversion[self.type]
        self._location = location
        self._board = board

    def __repr__(self):
        return f"<{self.__class__.__name__} type='{self.type}' location: '{self._location}'"

    @property
    def location(self) -> int:
        """Returns the location on the board the piece is at"""
        return self._location

    @location.setter
    def location(self, new_location: int):
        if not isinstance(new_location, int):
            raise TypeError("The location must be an integer")

        self.move(new_location)

    def move(self, new_location: int, /):
        """Moves the piece to the given location

        Parameters
        ----------
        new_location: `int`
            the location the piece should be moved to

        Raises
        ----------
        TypeError
            Invalid location given
        LocationAlreadyTaken
            The location already has a piece there
        """

        if new_location < 0 or new_location > 32:
            raise TypeError("The location must be inbetween 0 and 32")
        if not isinstance(self._board.pieces[new_location], EmptySpace):
            raise LocationAlreadyTaken(new_location)

        self._board.pieces[self._location] = EmptySpace()
        self._board.pieces[new_location] = self
        self._location = new_location

    def promote(self) -> None:
        """Promotes the piece to a queen

        Raises
        ----------
        UnableToPromote
            The piece is already a queen, and thus can not be promoted anymore
        """

        if isinstance(self, QueenPiece):
            raise UnableToPromote()

        new_piece = QueenPiece(
            _type=self.type, location=self._location, board=self._board  # type: ignore
        )
        self._board.pieces[self._location] = new_piece

    def demote(self) -> None:
        """Demotes a piece from a queen

        Raises
        ----------
        UnableToDemote
            This piece is already a normal piece, and thus can not be demoted anymore
        """

        if isinstance(self, PlayingPiece):
            raise UnableToDemote()

        new_piece = PlayingPiece(
            _type=self.type, location=self._location, board=self._board
        )
        self._board.pieces[self._location] = new_piece


class QueenPiece(PlayingPiece):
    _raw_conversion = {"black": "q", "red": "k"}


class EmptySpace:
    raw = "_"


class CheckersGame:
    __slots__ = ["_http", "pieces"]

    def __init__(self, *, http_client: HTTPClient):
        """Starts a checkers game

        It is not recommended to start this yourself

        Parameters
        ----------
        http_client: `ciberedev.http.HTTPClient`
            The HTTPClient

        Attributes
        ----------
        pieces: list[Union[`PlayingPiece`, `EmptySpace`, `QueenPiece`]]
            A list of all the pieces in order
        """

        self.pieces: list[Union[PlayingPiece, EmptySpace, QueenPiece]] = []
        self._http = http_client

        for i in range(8):
            self.pieces.append(PlayingPiece(_type="black", location=i, board=self))
        for i in range(16):
            self.pieces.append(EmptySpace())
        for i in range(8):
            self.pieces.append(PlayingPiece(_type="red", location=i, board=self))

    async def get_piece_at(
        self, index: int
    ) -> Optional[Union[PlayingPiece, QueenPiece]]:
        """Gets a piece at the given index

        Parameters
        ----------
        index: `int`
            The index to get the piece at

        Returns
        ----------
        Optional[Union[`PlayingPiece`, `QueenPiece`]]
        """

        piece = self.pieces[index]
        if isinstance(piece, EmptySpace):
            return None
        else:
            return piece

    @classmethod
    def from_pattern(cls, *, pattern: str, http_client: HTTPClient) -> Self:
        """Starts a chess game from a given pattern

        It is not recommended to start this yourself

        Parameters
        ----------
        pattern: str
            The pattern to set the board at
        http_client: `ciberedev.http.HTTPClient`
            The HTTPClient

        Attributes
        ----------
        pieces: list[Union[`PlayingPiece`, `EmptySpace`, `QueenPiece`]]
            A list of all the pieces in order
        """
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
        """Returns the pattern the current board is at

        Returns
        ----------
        str
        """

        return "".join(piece.raw for piece in self.pieces)

    async def generate_board(self) -> File:
        """Generates the boards image

        Returns
        ----------
        ciberedev.file.File
        """

        pattern = await self.to_pattern()
        raw = await self._http.get_checkers_board(pattern)
        file = File(raw_bytes=raw)
        return file
