import random
from socket import socket

from sqids import Sqids
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from chessinator_2000.gamestate import GameState, PieceColor, Square


class LANHostScreen(ModalScreen[socket | None]):
    DEFAULT_CSS = """
    LANHostScreen {
        align: center middle;
        content-align: center middle;
    }
    """

    def __init__(
        self, name: str | None = None, id: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(name, id, classes)
        self.host_id = Sqids().encode(
            [
                random.randint(0, 9),
                random.randint(0, 9),
                random.randint(0, 9),
                random.randint(0, 9),
            ]
        )

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"Waiting for connections. Host id: {self.host_id}", id="status"),
            Button("Cancel", id="lanHostScreen-cancel", variant="error"),
            Button("Play", id="lanHostScreen-play", variant="primary", disabled=True),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "lanHostScreen-cancel":
            self.dismiss(None)
        else:
            self.dismiss(None)


class LANPlayer:
    def __init__(self, app: App, color: PieceColor):
        self.socket: socket | None = None
        self.app = app
        self.color = color

        def on_dismiss(sock: socket | None):
            self.socket = sock

        self.app.push_screen(LANHostScreen(), on_dismiss)

    def handle_update_game(self, game: GameState) -> None:
        # TODO: implement net code

        pass

    def handle_update_selected_square(self, square: Square | None) -> None:
        pass

    def handle_update_chosen_square(self, square: Square | None) -> None:
        pass
