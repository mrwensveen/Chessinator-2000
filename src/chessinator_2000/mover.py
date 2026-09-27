import random
from collections import namedtuple
from typing import Protocol

from chessinator_2000.db.game_db import find_game_results
from chessinator_2000.gamestate import GameState, get_possible_moves
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
            if (result := next(r for r in db_results if r == str(move)))
        }

        scored: frozendict[GameState, float] = frozendict() | {
            move: 0.5
            if (f := found.get(move, None)) is None
            else self.score(**f._asdict())
            for move in moves
        }

        grouped = groupby(scored.items(), lambda gs: gs[1], lambda gs: gs[0])

    def score(self, *, white_wins: int, black_wins: int, num_played: int, **_) -> float:
        return 0.5
