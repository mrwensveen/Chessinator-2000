from collections.abc import Iterable

from textual.app import App
from textual.message import Message

from chessinator_2000.gamestate import (
    GameState,
    PieceColor,
    Square,
    get_occupant,
    get_possible_moves,
)
from chessinator_2000.mover import Mover
from chessinator_2000.utils import groupby


class PlayerMoved(Message):
    def __init__(self, move: GameState | None) -> None:
        super().__init__()
        self.move = move


class PlayerChoicesChanged(Message):
    def __init__(self, squares: list[Square]) -> None:
        super().__init__()
        self.squares = squares


class Player:
    game: GameState | None = None
    selected_quare: Square | None = None
    moves: frozendict[Square, Iterable[GameState]] = frozendict()

    def __init__(self, app: App, color: PieceColor):
        self.app = app
        self.color = color

        app.watch(app, "game", self.handle_update_game, init=False)
        app.watch(
            app, "selected_square", self.handle_update_selected_square, init=False
        )
        app.watch(app, "chosen_square", self.handle_update_chosen_square, init=False)

    def handle_update_game(self, game: GameState) -> None:
        if game.turn == self.color:
            self.app.log(f"Player: {self.color}")

        self.game = game
        self.selected_quare = None
        self.moves = (
            frozendict()
            if game.turn != self.color
            else groupby(
                get_possible_moves(game),
                lambda move: next(iter(game.board.keys() - move.board.keys())),
            )
        )

    def handle_update_selected_square(self, square: Square) -> None:
        if (game := self.game) is None or game.turn != self.color:
            return

        self.selected_quare = square
        selected_moves = self.moves.get(square, [])

        def _color_squares(g: GameState) -> set[Square]:
            return {s for s, p in g.board.items() if p.color == self.color}

        game_squares = _color_squares(game)
        choices = [
            next(iter(_color_squares(move) - game_squares)) for move in selected_moves
        ]
        self.app.post_message(PlayerChoicesChanged(choices))

    def handle_update_chosen_square(self, square: Square) -> None:
        if (selected_square := self.selected_quare) is None:
            return

        move = next(
            iter(
                move
                for move in self.moves.get(selected_square, [])
                if (occupant := get_occupant(move, square)) is not None
                and occupant.color == self.color
            ),
            None,
        )
        self.app.post_message(PlayerMoved(move))


class Cpu:
    def __init__(self, app: App, color: PieceColor, mover: Mover):
        self.app = app
        self.color = color
        self.mover = mover

        app.watch(app, "game", self.handle_update_game, init=False)

    def handle_update_game(self, game: GameState) -> None:
        if game.turn != self.color:
            return

        self.app.log(f"Cpu({type(self.mover).__name__}): {self.color}")

        def do_move():
            move = self.mover.move(game)
            self.app.post_message(PlayerMoved(move))

        self.app.set_timer(1, do_move)
