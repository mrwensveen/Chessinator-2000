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


class PlayerMover:
    def move(self, game: GameState) -> GameState | None: ...
