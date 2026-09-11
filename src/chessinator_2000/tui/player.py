from textual.app import App

from chessinator_2000.gamestate import GameState, Piece, PieceColor, PieceKind
from chessinator_2000.mover import Mover
from chessinator_2000.parser import Game


class Player(Mover):
    def __init__(self, app: App):
        self.app = app

    def move(self, game: GameState) -> GameState | None:
        self.app.log("move")
        return game.skip_turn()
