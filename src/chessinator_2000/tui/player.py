from typing import TYPE_CHECKING

from chessinator_2000.gamestate import GameState, PieceColor
from chessinator_2000.mover import Mover

if TYPE_CHECKING:
    from chessinator_2000.tui.app import Chessinator2000


class Player:
    def __init__(self, app: Chessinator2000, color: PieceColor):
        self.app = app
        self.color = color

        app.watch(app, "game", self.update_game, init=False)

    def update_game(self, game: GameState) -> None:
        if game.turn != self.color:
            return

        self.app.log(f"Player: {self.color}")


class Cpu:
    def __init__(self, app: Chessinator2000, color: PieceColor, mover: Mover):
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
            self.app.game = move

        self.app.set_timer(1.5, do_move)
