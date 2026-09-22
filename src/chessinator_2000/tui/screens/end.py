from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from chessinator_2000.gamestate import GameState


class EndScreen(ModalScreen):
    DEFAULT_CSS = """
    EndScreen {
        align: center middle;
        content-align: center middle;
    }
    """

    def __init__(
        self,
        game: GameState | None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.game = game

    def compose(self) -> ComposeResult:
        status = (
            "draw"
            if self.game is None or self.game.status == "in_progress"
            else self.game.status
        )
        yield Grid(
            Label(status.capitalize(), id="status"),
            Button("Quit", id="quit", variant="error"),
            Button("Play again", id="restart", variant="primary", disabled=True),
            id="dialog",
        )
