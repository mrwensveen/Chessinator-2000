import random
from typing import Protocol

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
