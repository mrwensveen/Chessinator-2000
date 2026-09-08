from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header

from chessinator_2000.gamestate import GameState


class Chessinator2000(App):
    TITLE = "Chessinator 2000!"

    game = reactive[GameState | None](None)

    def compose(self) -> ComposeResult:
        yield Header()

    def on_button_pressed(self) -> None:
        self.exit()

    def watch_game(self, game: GameState) -> None:
        return
