# import sqlite3

# conn = sqlite3.connect(':memory:')
# cursor = conn.cursor()
# cursor.execute('CREATE TABLE users (name TEXT, age INTEGER)')
# cursor.execute("INSERT INTO users VALUES ('Tobias', 28)")
# conn.commit()

# cursor.execute('SELECT * FROM users')
# result = cursor.fetchone()
# print(f'User: {result[0]}, Age: {result[1]}')

# TODO: ContextManager stuff?

import random
from typing import Protocol

from chessinator_2000.gamestate import GameState, get_possible_moves
from chessinator_2000.utils import groupby


class Mover(Protocol):
    def move(self, game: GameState) -> GameState | None: ...


class RandomMover:
    def move(self, game: GameState) -> GameState | None:
        moves = list(get_possible_moves(game))

        if len(moves) > 0:
            # Pick a random move
            move = random.choice(moves)
            return move
        else:
            return None


class FirstMover:
    def move(self, game: GameState) -> GameState | None:
        return next(iter(get_possible_moves(game)), None)


class RandomPieceMover:
    def move(self, game: GameState) -> GameState | None:
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
