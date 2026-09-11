from textual.app import App, ComposeResult
from textual.containers import Center, CenterMiddle
from textual.reactive import reactive
from textual.widgets import Button, Header

from chessinator_2000.gamestate import GameState, PieceColor
from chessinator_2000.mover import Mover
from chessinator_2000.parser import Game
from chessinator_2000.tui.chessboard import Chessboard


class Chessinator2000(App):
    TITLE = "Chessinator 2000!"

    game: reactive[GameState | None] = reactive(None)

    def __init__(self, game: GameState, white_mover: Mover, black_mover: Mover) -> None:
        super().__init__()
        self.game = game
        self.movers: frozendict[PieceColor, Mover] = frozendict() | {
            PieceColor.WHITE: white_mover,
            PieceColor.BLACK: black_mover,
        }

    def compose(self) -> ComposeResult:
        yield Header()
        with CenterMiddle():
            yield Chessboard().data_bind(Chessinator2000.game)
        with Center():
            yield Button(id="reset", label="Restart")

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(0.05, self.update_game)

    def on_button_pressed(self) -> None:
        self.game = Game("""
            |r̃|ñ|b̃|q̃|k̃|b̃|ñ|r̃|
            |p̃|p̃|p̃|p̃|p̃|p̃|p̃|p̃|
            | | | | | | | | |
            | | | | | | | | |
            | | | | | | | | |
            | | | | | | | | |
            |P̃|P̃|P̃|P̃|P̃|P̃|P̃|P̃|
            |R̃|Ñ|B̃|Q̃|K̃|B̃|Ñ|R̃|
            turn=WHITE
        """)

        self.update_timer.stop()
        self.update_timer = self.set_interval(0.05, self.update_game)

    def update_game(self) -> None:
        if self.game is None:
            return

        if len(self.game.board) == 2:
            self.update_timer.stop()

        move = self.movers[self.game.turn].move(self.game)

        if move is not None:
            self.game = move
        else:
            self.update_timer.stop()

    # def on_button_pressed(self) -> None:
    #     self.exit()

    # def watch_game(self, game: GameState) -> None:
    #     return
