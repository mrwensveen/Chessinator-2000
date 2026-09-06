import re
from typing import Literal, cast, overload

from chessinator_2000.gamestate import GameState, Piece, PieceColor, PieceKind, Square

PC_KIND = Literal["p", "P", "r", "R", "n", "N", "b", "B", "q", "Q", "k", "K"]


def Pc(s: PC_KIND, moved=False) -> Piece:
    upper = s.upper()
    kind = (
        PieceKind.KNIGHT
        if upper == "N"
        else next(
            kind
            for kind in PieceKind
            if kind.name[0] == upper and kind != PieceKind.KNIGHT
        )
    )
    return Piece(PieceColor.WHITE if s == upper else PieceColor.BLACK, kind, moved)


def Sq(s: str) -> Square:
    if len(s) != 2:
        raise ValueError

    x = ord(s[0]) - 96
    y = int(s[1])

    if not (1 <= x <= 8 and 1 <= y <= 8):
        raise ValueError

    return (x, y)


@overload
def Game(board: list[str], turn=PieceColor.WHITE) -> GameState: ...


@overload
def Game(board: str) -> GameState: ...


def Game(board: str | list[str], turn=PieceColor.WHITE) -> GameState:
    return (
        _game_from_str(board)
        if isinstance(board, str)
        else _game_from_list(board, turn)
    )


def _game_from_str(board: str) -> GameState:
    split = board.strip("\n").splitlines() if isinstance(board, str) else board
    ranks = [rank.lstrip().replace("|", "") for rank in split[:8]]
    turn = (
        PieceColor.BLACK
        if len(split) > 8 and "turn=BLACK" in split[8]
        else PieceColor.WHITE
    )

    return _game_from_list(ranks, turn)


def _game_from_list(ranks: list[str], turn: PieceColor) -> GameState:
    # Encode unmoved pieces (p + \ud1fa) as a single character
    re_unmoved = re.compile("(.)\u1dfa")

    def encode_unmoved(match: re.Match) -> str:
        return chr(ord(match.group(1)) + 0x1DFA)

    def decode(enc: int, moved: bool) -> PC_KIND:
        return cast(PC_KIND, chr(enc - (0 if moved else 0x1DFA)))

    b: frozendict[Square, Piece] = frozendict() | {
        (x + 1, 8 - y): Pc(kind, moved)
        for y, rank in enumerate(ranks[:8])
        for x, s in enumerate(re_unmoved.sub(encode_unmoved, rank)[:8])
        if s not in " ↑↓"
        and (enc := ord(s)) > 0
        and ((moved := enc <= 0x1DFA) or True)
        and (kind := decode(enc, moved))
    }

    # Decode en passant
    sq: Square | None = next(
        (
            (x + 1, 8 - y)
            for y, rank in enumerate(ranks[:8])
            if (x := max(rank.find("↑"), rank.find("↓"))) > -1
        ),
        None,
    )
    en_passant: tuple[Square, Square] | None = (
        (sq, (sq[0], sq[1] + direction))
        if sq is not None
        and (direction := (1 if ranks[8 - sq[1]][sq[0] - 1] == "↑" else -1))
        else None
    )

    return GameState(b, turn, en_passant)
