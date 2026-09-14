from textual.app import App
from textual.message import Message

from chessinator_2000.gamestate import GameState, PieceColor
from chessinator_2000.mover import Mover


class MoveMessage(Message):
    def __init__(self, move: GameState | None) -> None:
        super().__init__()
        self.move = move

class Player:
    def __init__(self, app: App, color: PieceColor):
        self.app = app
        self.color = color

        app.watch(app, "game", self.update_game, init=False)

    def update_game(self, game: GameState) -> None:
        if game.turn != self.color:
            return

        self.app.log(f"Player: {self.color}")


class Cpu:
    def __init__(self, app: App, color: PieceColor, mover: Mover):
        self.app = app
        self.color = color
        self.mover = mover
        app.watch(app, "game", self.update_game, init=False)

    def update_game(self, game: GameState) -> None:
        if game.turn != self.color:
            return

        self.app.log(f"Cpu({type(self.mover).__name__}): {self.color}")

        def do_move():
            move = self.mover.move(game)
            self.app.post_message(MoveMessage(move))

        self.app.set_timer(1, do_move)
