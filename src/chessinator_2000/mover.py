import random
from typing import Protocol

from chessinator_2000.db.game_db import DbGameResult, find_game_results
from chessinator_2000.gamestate import GameState, Move, PieceColor, get_possible_moves
from chessinator_2000.utils import groupby


class Mover(Protocol):
    def __init__(self, color: PieceColor) -> None: ...
    def move(self, game: GameState) -> tuple[GameState, float] | None: ...


class RandomMover:
    def __init__(self, color: PieceColor) -> None:
        pass

    def move(self, game: GameState) -> tuple[GameState, float] | None:
        if (len(game.board)) <= 2:
            return None

        moves = [move for _, move in get_possible_moves(game)]

        if len(moves) > 0:
            # Pick a random move
            move = random.choice(moves)
            return (move, 0.0)
        else:
            return None


class FirstMover:
    def __init__(self, color: PieceColor) -> None:
        pass

    def move(self, game: GameState) -> tuple[GameState, float] | None:
        if (len(game.board)) <= 2:
            return None

        move = next(iter(get_possible_moves(game)), None)
        return move if move is None else (move[1], 0.0)


class RandomPieceMover:
    def __init__(self, color: PieceColor) -> None:
        pass

    def move(self, game: GameState) -> tuple[GameState, float] | None:
        if (len(game.board)) <= 2:
            return None

        moves = list(get_possible_moves(game))

        if len(moves) > 0:
            # Get the move's leaving position by removing all resulting positions from the original board
            origins = groupby(moves, lambda move: move[0], lambda move: move[1])
            square = random.choice(list(origins.keys()))
            return (random.choice(list(origins[square])), 0.0)
        else:
            return None


class DatabaseMover:
    def __init__(self, color: PieceColor) -> None:
        self.color = color

    def move(self, game: GameState) -> tuple[GameState, float] | None:
        if (len(game.board)) <= 2:
            return None

        moves = list(get_possible_moves(game))

        db_results: frozenset[DbGameResult] = frozenset(
            map(
                DbGameResult._make,
                find_game_results(game.turn.flipped(), (move for _, move in moves)),
            )
        )

        found: frozendict[Move, DbGameResult] = frozendict() | {
            move: result
            for move in moves
            if (
                result := next(
                    (r for r in db_results if r.game_state == str(move[1])), None
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

        best_moves = list(first[1])
        score = first[0]

        # choice = random.choice(best_moves)

        origins = groupby(best_moves, lambda move: move[0], lambda move: move[1])
        square = random.choice(list(origins.keys()))
        choice = random.choice(list(origins[square]))

        return (choice, score)

    def score(self, *, white_wins: int, black_wins: int, num_played: int) -> float:
        score = (
            float(white_wins - black_wins)
            / max(1.0, float(num_played))
            * float(self.color.value)
        )
        return score
