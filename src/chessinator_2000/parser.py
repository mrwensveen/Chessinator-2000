import re
from typing import Literal, cast

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


def Game(board: str) -> GameState:
    lines = board.strip("\n").splitlines()
    ranks = [rank.lstrip().replace("|", "") for rank in lines[:8]]
    turn = (
        PieceColor.BLACK
        if len(lines) > 8 and "turn=BLACK" in lines[8]
        else PieceColor.WHITE
    )

    return _game_from_list(ranks, turn)


def _game_from_list(ranks: list[str], turn: PieceColor) -> GameState:
    # Replace unmoved pieces ('P' + \u0303 = 'P̃') by a single character chr(ord('P') + 0x0303)
    # (this is not a valid renderable character), while leaving moved pieces untouched.
    re_unmoved = re.compile("(.)\u0303")

    def encode_unmoved(match: re.Match) -> str:
        return chr(ord(match.group(1)) + 0x0303)

    def decode(enc: int, moved: bool) -> PC_KIND:
        return cast(PC_KIND, chr(enc - (0 if moved else 0x0303)))

    b: frozendict[Square, Piece] = frozendict() | {
        (x + 1, 8 - y): Pc(kind, moved)
        for y, rank in enumerate(ranks[:8])
        for x, s in enumerate(re_unmoved.sub(encode_unmoved, rank)[:8])
        if s not in " ↑↓"
        and (enc := ord(s)) > 0
        and ((moved := enc <= 0x0303) or True)
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
