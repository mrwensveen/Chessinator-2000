from itertools import chain
from typing import Protocol

from textual.app import App
from textual.message import Message

from chessinator_2000.gamestate import (
    GameState,
    PieceColor,
    Square,
    get_occupant,
    get_piece_moves,
    get_possible_moves,
)
from chessinator_2000.mover import Mover


class PlayerMoved(Message):
    def __init__(self, move: GameState | None, message: object | None = None) -> None:
        super().__init__()
        self.move = move
        self.message = message


class PlayerChoicesChanged(Message):
    def __init__(self, squares: frozenset[Square]) -> None:
        super().__init__()
        self.squares = squares


class Player(Protocol):
    def handle_update_game(self, game: GameState) -> None: ...
    def handle_update_selected_square(self, square: Square | None) -> None: ...
    def handle_update_chosen_square(self, square: Square | None) -> None: ...


class UserPlayer:
    game: GameState | None = None
    selected_quare: Square | None = None
    choice_moves: tuple[GameState, ...] = ()

    def __init__(self, app: App, color: PieceColor):
        self.app = app
        self.color = color

    def handle_update_game(self, game: GameState) -> None:
        self.game = game
        self.selected_quare = None

        # TODO: This is very inefficient, probably
        if game.turn == self.color and (
            len(game.board) <= 2 or len(list(get_possible_moves(game))) == 0
        ):
            self.app.post_message(PlayerMoved(None))

    def handle_update_selected_square(self, square: Square | None) -> None:
        if self.game is None or self.game.turn != self.color or square is None:
            return

        if (
            (game := self.game) is None
            or game.turn != self.color
            or (piece := get_occupant(game, square)) is None
        ):
            return

        self.selected_quare = square

        piece_moves = tuple(get_piece_moves(game, square, piece))
        self.choice_moves = piece_moves

        def _color_squares(g: GameState) -> set[Square]:
            return {s for s, p in g.board.items() if p.color == self.color}

        game_squares = _color_squares(game)
        choices = frozenset(
            chain.from_iterable(
                iter(_color_squares(move) - game_squares) for move in piece_moves
            )
        )
        self.app.post_message(PlayerChoicesChanged(choices))

    def handle_update_chosen_square(self, square: Square | None) -> None:
        if self.game is None or self.game.turn != self.color or square is None:
            return

        if not self.choice_moves:
            return

        move = next(
            iter(
                move
                for move in self.choice_moves
                if (occupant := get_occupant(move, square)) is not None
                and occupant.color == self.color
            ),
            None,
        )
        self.app.post_message(PlayerMoved(move))


class CpuPlayer:
    def __init__(self, app: App, color: PieceColor, mover: Mover):
        self.app = app
        self.color = color
        self.mover = mover
        self.delay = 1.0

    def handle_update_game(self, game: GameState) -> None:
        if game.turn != self.color:
            return

        def do_move():
            move = self.mover.move(game) if len(game.board) >= 2 else None
            self.app.post_message(PlayerMoved(move, type(self.mover).__name__))

        self.app.set_timer(self.delay, do_move)

    def handle_update_selected_square(self, square: Square | None) -> None:
        pass

    def handle_update_chosen_square(self, square: Square | None) -> None:
        pass
