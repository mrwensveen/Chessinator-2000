import random
from collections import namedtuple
from typing import Protocol

from chessinator_2000.db.game_db import find_game_results
from chessinator_2000.gamestate import GameState, PieceColor, get_possible_moves
from chessinator_2000.utils import groupby


class Mover(Protocol):
    def move(self, game: GameState) -> GameState | None: ...


class RandomMover:
    def move(self, game: GameState) -> GameState | None:
        if (len(game.board)) <= 2:
            return None

        moves = list(get_possible_moves(game))

        if len(moves) > 0:
            # Pick a random move
            move = random.choice(moves)
            return move
        else:
            return None


class FirstMover:
    def move(self, game: GameState) -> GameState | None:
        if (len(game.board)) <= 2:
            return None
        return next(iter(get_possible_moves(game)), None)


class RandomPieceMover:
    def move(self, game: GameState) -> GameState | None:
        if (len(game.board)) <= 2:
            return None

        moves = list(get_possible_moves(game))

        if len(moves) > 0:
            # Get the move's leaving position by removing all resulting positions from the original board
            origins = groupby(
                moves, lambda move: next(iter(game.board.keys() - move.board.keys()))
            )
            square = random.choice(list(origins.keys()))
            return random.choice(list(origins[square]))
        else:
            return None


DbGameResult = namedtuple(
    "DbGameResult", ["game_state", "white_wins", "black_wins", "num_played"]
)


class DatabaseMover:
    def __init__(self, color: PieceColor) -> None:
        self.color = color

    def move(self, game: GameState) -> GameState | None:
        if (len(game.board)) <= 2:
            return None

        moves = list(get_possible_moves(game))

        db_results: frozenset[DbGameResult] = frozenset(
            map(DbGameResult._make, find_game_results(game.turn.flipped(), moves))
        )

        found = frozendict() | {
            move: result
            for move in moves
            if (
                result := next(
                    (r for r in db_results if r.game_state == str(move)), None
                )
            )
            is not None
        }

        grouped = groupby(
            moves,
            lambda m: (
                0.0
                if (f := found.get(m, None)) is None
                else self.score(
                    white_wins=f.white_wins,
                    black_wins=f.black_wins,
                    num_played=f.num_played,
                )
            ),
        )

        first = next(
            iter(sorted(grouped.items(), key=lambda i: i[0], reverse=True)), None
        )

        if first is None:
            return None

        choice = random.choice(list(first[1]))
        return choice

    def score(self, *, white_wins: int, black_wins: int, num_played: int) -> float:
        return (white_wins - black_wins) / min(1, num_played) * self.color.value
