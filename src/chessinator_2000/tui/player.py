from textual.app import App
from textual.message import Message

from chessinator_2000.gamestate import GameState, PieceColor, Square, get_possible_moves
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

    def __init__(self, app: App, color: PieceColor):
        self.app = app
        self.color = color

        app.watch(app, "game", self.handle_update_game, init=False)
        app.watch(
            app, "selected_square", self.handle_update_selected_square, init=False
        )

    def handle_update_game(self, game: GameState) -> None:
        if game.turn != self.color:
            return

        self.app.log(f"Player: {self.color}")
        self.game = game

    def handle_update_selected_square(self, square: Square) -> None:
        game = self.game
        if game is None:
            return

        moves = list(get_possible_moves(game))
        origins = groupby(
            moves,
            lambda move: next(iter(game.board.keys() - move.board.keys())),
            lambda move: next(iter(move.board.keys() - game.board.keys())),
        )

        choices = list(origins.get(square, []))
        self.app.post_message(PlayerChoicesChanged(choices))


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
