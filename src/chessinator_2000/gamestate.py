from collections.abc import Callable, Generator, Iterable
from dataclasses import dataclass
from enum import Enum
from itertools import chain
from typing import Literal

from python_fp_flow.flow import Flow

type Square = tuple[int, int]


class PieceKind(Enum):
    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    QUEEN = 5
    KING = 6


class PieceColor(Enum):
    WHITE = 1
    BLACK = -1

    def flipped(self) -> PieceColor:
        return PieceColor(self.value * -1)


@dataclass(frozen=True)
class Piece:
    color: PieceColor
    kind: PieceKind
    moved: bool = False

    def promote(self, kind: PieceKind) -> Piece:
        return Piece(self.color, kind, self.moved)

    def __str__(self):
        s = "N" if self.kind == PieceKind.KNIGHT else self.kind.name[0]
        return s.lower() if self.color == PieceColor.BLACK else s


@dataclass(frozen=True)
class GameState:
    board: frozendict[Square, Piece]
    turn: PieceColor
    en_passant: tuple[Square, Square] | None = None

    @property
    def status(self) -> Literal["in_progress", "stalemate", "checkmate"]:
        return (
            "in_progress"
            if any(get_possible_moves(self))
            else "checkmate"
            if _is_check(self.skip_turn())
            else "stalemate"
        )

    def move(self, piece: Piece, src: Square, dst: Square, next_turn=True) -> GameState:
        # Mark an en-passant possibility if the current player's pawn moves two forward as its initial
        # move
        en_passant: tuple[Square, Square] | None = (
            ((src[0], src[1] + piece.color.value), dst)
            if piece.kind == PieceKind.PAWN
            and not piece.moved
            and dst[1] == src[1] + 2 * piece.color.value
            else None
        )

        board = (
            Flow(self.board)
            # Delete the piece from src
            >> _delete(src)
            # Delete the opponent's pawn if it left an en-passant possibility and the current player's
            # pawn is moved to that spot
            >> (
                _delete(self.en_passant[1])
                if piece.kind == PieceKind.PAWN
                and self.en_passant is not None
                and dst == self.en_passant[0]
                else _identity
            )
            # Add the piece to the new position
            >> _set(dst, Piece(piece.color, piece.kind, moved=True))
        ).value()

        return GameState(
            board=board,
            turn=self.turn.flipped() if next_turn else self.turn,
            en_passant=en_passant,
        )

    def skip_turn(self) -> GameState:
        return GameState(
            board=self.board, turn=self.turn.flipped(), en_passant=self.en_passant
        )

    def __str__(self):
        board_str = "\n".join(
            f"|{
                '|'.join(
                    f'\033[{"91m" if piece.color == PieceColor.WHITE else "94m"}{piece}{"\u20f0" if not piece.moved else ""}\033[0m'
                    if (piece := get_occupant(self, (x, y))) is not None
                    else '.'
                    if self.en_passant is not None and self.en_passant[0] == (x, y)
                    else ' '
                    for x in range(1, 9)
                )
            }|"
            for y in range(8, 0, -1)
        )

        return f"{board_str}\nturn={self.turn.name}\n"


def get_occupant(game: GameState, position: Square | None) -> Piece | None:
    return None if position is None else game.board.get(position)


def get_attackers(game: GameState, position: Square) -> Iterable[tuple[Square, Piece]]:
    # If the current player already occupies the position, there are no attackers
    if (
        occupant := get_occupant(game, position)
    ) is not None and occupant.color == game.turn:
        return frozendict()

    # All moves that cause the position to be taken by the current player
    all_moves = get_possible_moves(game, check_check=False)
    moves = (
        move
        for move in all_moves
        if (occupant := get_occupant(move, position)) is not None
        and occupant.color == game.turn
    )

    # Get attacker positions by deleting all new positions from the current board, leaving only the attacker's origin
    points = chain.from_iterable(
        iter(_delete(*move.board.keys())(game.board).keys()) for move in moves
    )

    # Get the attacking pieces from the current board and return as frozendict
    return (
        (point, occupant)
        for point in points
        if (occupant := get_occupant(game, point)) is not None
    )


def get_pieces(
    game: GameState, color: PieceColor, kind: PieceKind
) -> frozendict[Square, Piece]:
    return frozendict() | {
        k: v for k, v in game.board.items() if v.color == color and v.kind == kind
    }


def get_possible_moves(
    game: GameState, check_check: bool = True
) -> Iterable[GameState]:
    # print(f"\033[92m{game}\033[0m", file=sys.stderr)

    # All moves, including those that put the king in an attacked position
    potential_moves = chain.from_iterable(
        get_piece_moves(game, position, piece)
        for position, piece in game.board.items()
        if piece.color == game.turn
    )

    # Don't check for check
    if not check_check:
        return potential_moves

    # Remove the moves that result in check
    return (move for move in potential_moves if not _is_check(move))


def _is_check(game: GameState) -> bool:
    # print(f"\033[92m{game}\033[0m", file=sys.stderr)
    king_positions = get_pieces(game, game.turn.flipped(), PieceKind.KING).keys()
    attackers = any(
        chain.from_iterable(
            get_attackers(game, position) for position in king_positions
        )
    )

    return attackers


def get_piece_moves(game: GameState, position: Square, piece: Piece) -> list[GameState]:
    match piece.kind:
        case PieceKind.PAWN:
            return pawn_moves(game, position)
        case PieceKind.KNIGHT:
            return knight_moves(game, position)
        case PieceKind.KING:
            return king_moves(game, position)
        case PieceKind.QUEEN | PieceKind.ROOK | PieceKind.BISHOP:
            return slide_moves(game, position)
        case _:
            return []


def pawn_moves(game: GameState, position: Square) -> list[GameState]:
    piece = get_occupant(game, position)
    if piece is None or piece.kind != PieceKind.PAWN:
        return []

    (x, y) = position
    positions: list[Square | None] = [
        (x, y + piece.color.value),
        (x, y + 2 * piece.color.value) if not piece.moved else None,
        (x - 1, y + piece.color.value) if x >= 2 else None,
        (x + 1, y + piece.color.value) if x <= 7 else None,
    ]

    occupants = [get_occupant(game, p) for p in positions]

    possible = [
        pos
        for pos in [
            positions[0] if occupants[0] is None else None,
            positions[1] if occupants[0] is None and occupants[1] is None else None,
            positions[2]
            if positions[2] is not None
            and (
                occupants[2] is not None
                and occupants[2].color != piece.color
                or (game.en_passant is not None and positions[2] == game.en_passant[0])
            )
            else None,
            positions[3]
            if positions[3] is not None
            and (
                occupants[3] is not None
                and occupants[3].color != piece.color
                or (game.en_passant is not None and positions[3] == game.en_passant[0])
            )
            else None,
        ]
        if pos is not None
    ]

    # Promotions
    promotion_row = piece.color.flipped().value % 9

    def kinds(dst: Square):
        return (
            [PieceKind.QUEEN, PieceKind.ROOK, PieceKind.BISHOP, PieceKind.KNIGHT]
            if dst[1] == promotion_row
            else [piece.kind]
        )

    return list(
        chain.from_iterable(
            (game.move(piece.promote(kind), position, dst) for kind in kinds(dst))
            for dst in possible
        )
    )


def knight_moves(game: GameState, position: Square) -> list[GameState]:
    piece = get_occupant(game, position)
    if piece is None or piece.kind != PieceKind.KNIGHT:
        return []

    (x, y) = position
    positions: list[Square | None] = [
        (x + 1, y + 2) if x <= 7 and y <= 6 else None,
        (x + 2, y + 1) if x <= 6 and y <= 7 else None,
        (x + 2, y - 1) if x <= 6 and y >= 2 else None,
        (x + 1, y - 2) if x <= 7 and y >= 3 else None,
        (x - 1, y - 2) if x >= 2 and y >= 3 else None,
        (x - 2, y - 1) if x >= 3 and y >= 2 else None,
        (x - 2, y + 1) if x >= 3 and y <= 7 else None,
        (x - 1, y + 2) if x >= 1 and y <= 6 else None,
    ]

    possible = [
        p
        for p in positions
        if p is not None
        and (
            (occupant := get_occupant(game, p)) is None or occupant.color != piece.color
        )
    ]

    return [game.move(piece, position, dst) for dst in possible if dst is not None]


def king_moves(game: GameState, position: Square) -> list[GameState]:
    piece = get_occupant(game, position)
    if piece is None or piece.kind != PieceKind.KING:
        return []

    (x, y) = position
    positions: list[Square | None] = [
        (x + 1, y) if x <= 7 else None,
        (x - 1, y) if x >= 2 else None,
        (x, y + 1) if y <= 7 else None,
        (x, y - 1) if y >= 2 else None,
        (x + 1, y + 1) if x <= 7 and y <= 7 else None,
        (x + 1, y - 1) if x <= 7 and y >= 2 else None,
        (x - 1, y + 1) if x >= 2 and y <= 7 else None,
        (x - 1, y - 1) if x >= 2 and y >= 2 else None,
    ]

    occupants = [(p, get_occupant(game, p)) for p in positions]

    possible = [
        pos if occupant is None or occupant.color != piece.color else None
        for pos, occupant in occupants
    ]

    def move_king(dst: Square):
        return game.move(piece, position, dst)

    moves = [move_king(dst) if dst is not None else None for dst in possible]

    # Castling is not allowed if king leaves or crosses check
    qs_rook = (
        rook
        if not piece.moved
        and (rook := _get_castle_rook(game, y, "QS")) is not None
        and not _is_check(game.skip_turn())
        and not _is_check(move_king((x - 1, y)))
        else None
    )
    ks_rook = (
        rook
        if not piece.moved
        and (rook := _get_castle_rook(game, y, "KS")) is not None
        and not _is_check(game.skip_turn())
        and not _is_check(move_king((x + 1, y)))
        else None
    )

    castlings = [
        # Castling QS
        move_king((x - 2, y)).move(qs_rook, (1, y), (4, y), next_turn=False)
        if qs_rook is not None
        else None,
        # Castling KS
        move_king((x + 2, y)).move(ks_rook, (8, y), (6, y), next_turn=False)
        if ks_rook is not None
        else None,
    ]

    return list(
        chain.from_iterable(
            (
                (move for move in moves if move is not None),
                (move for move in castlings if move is not None),
            )
        )
    )


_slide_directions: frozendict[PieceKind, frozenset[Square]] = frozendict() | {
    PieceKind.QUEEN: frozenset()
    | {(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)},
    PieceKind.ROOK: frozenset() | {(0, 1), (1, 0), (0, -1), (-1, 0)},
    PieceKind.BISHOP: frozenset() | {(1, 1), (1, -1), (-1, -1), (-1, 1)},
}


def slide_moves(game: GameState, position: Square) -> list[GameState]:
    piece = get_occupant(game, position)
    if piece is None or piece.kind not in [
        PieceKind.QUEEN,
        PieceKind.ROOK,
        PieceKind.BISHOP,
    ]:
        return []

    directions = _slide_directions.get(piece.kind, [])
    possible = chain.from_iterable(
        _slide(game, piece, position, direction) for direction in directions
    )

    return [game.move(piece, position, dst) for dst in possible]


def _slide(
    game: GameState, piece: Piece, position: Square, direction: Square
) -> Generator[Square]:
    x, y = (position[0] + direction[0], position[1] + direction[1])
    if x < 1 or x > 8 or y < 1 or y > 8:
        return

    occupant = get_occupant(game, (x, y))

    if occupant is None or occupant.color != piece.color:
        yield (x, y)

    if occupant is None:
        yield from _slide(game, piece, (x, y), direction)


def _get_castle_rook(
    game: GameState, rank: int, side: Literal["QS", "KS"]
) -> Piece | None:
    rook_file = 1 if side == "QS" else 8
    check_files = [2, 3, 4] if side == "QS" else [6, 7]
    castle_rook: Piece | None = (
        rook
        if (
            (rook := get_occupant(game, (rook_file, rank))) is not None
            and rook.kind == PieceKind.ROOK
            and rook.color == game.turn
            and not rook.moved
            and not [
                occupant
                for xx in check_files
                if (occupant := get_occupant(game, (xx, rank))) is not None
            ]
        )
        else None
    )

    return castle_rook


def _delete[K, V](*key: K) -> Callable[[frozendict[K, V]], frozendict[K, V]]:
    def fn(d: frozendict[K, V]) -> frozendict[K, V]:
        return frozendict((k, v) for k, v in d.items() if k not in key)  # pyright: ignore[reportCallIssue]

    return fn


def _set[K, V](key: K, value: V) -> Callable[[frozendict[K, V]], frozendict[K, V]]:
    def fn(d: frozendict[K, V]) -> frozendict[K, V]:
        return d | {key: value}

    return fn


def _identity[T](x: T, /) -> T:
    return x
