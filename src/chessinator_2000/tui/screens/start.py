from collections.abc import Callable

from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select

from chessinator_2000.gamestate import PieceColor
from chessinator_2000.mover import FirstMover, RandomMover, RandomPieceMover
from chessinator_2000.tui.player import Cpu, Player


class StartScreen(
    ModalScreen[
        tuple[Callable[[App, PieceColor], object], Callable[[App, PieceColor], object]]
    ]
):
    DEFAULT_CSS = """
    StartScreen {
        align: center middle;
        content-align: center middle;
    }
    """

    player_white: reactive[int] = reactive(0)
    player_black: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        player_options = [
            ("Player", 1),
            ("CPU Random move", 2),
            ("CPU Random piece", 3),
            ("CPU First move", 4),
        ]

        yield Grid(
            Label("Start a new game", id="question"),
            Select[int](player_options, prompt="White player", id="select_white"),
            Select[int](player_options, prompt="Black player", id="select_black"),
            Button("Quit", id="quit", variant="error"),
            Button("Start", id="start", variant="primary", disabled=True),
            id="dialog",
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        if not isinstance(value := event.value, int):
            value = 0

        match event.control.id:
            case "select_white":
                self.player_white = value
            case "select_black":
                self.player_black = value

        self.query_one("#start", Button).disabled = (
            self.player_white == 0 or self.player_black == 0
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.dismiss(
                (
                    self._create_player_factory(self.player_white),
                    self._create_player_factory(self.player_black),
                )
            )

    def _create_player_factory(
        self, option: int
    ) -> Callable[[App, PieceColor], object]:
        match option:
            case 1:
                return lambda app, color: Player(app, color)
            case 2:
                return lambda app, color: Cpu(app, color, RandomMover())
            case 3:
                return lambda app, color: Cpu(app, color, RandomPieceMover())
            case 4:
                return lambda app, color: Cpu(app, color, FirstMover())

        msg = f"Could not create player factory for option {option}"
        raise ValueError(msg)
