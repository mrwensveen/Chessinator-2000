from textual.app import App, ComposeResult
from textual.containers import Center, CenterMiddle
from textual.reactive import reactive
from textual.widgets import Button, Header

from chessinator_2000.gamestate import GameState, PieceColor
from chessinator_2000.mover import FirstMover, RandomMover, RandomPieceMover
from chessinator_2000.parser import Game
from chessinator_2000.tui.chessboard import Chessboard
from chessinator_2000.tui.player import Cpu, MoveMessage, Player

DEFAULT_GAME = Game("""
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


class Chessinator2000(App):
    TITLE = "Chessinator 2000!"

    game: reactive[GameState | None] = reactive(None)

    def __init__(self, game: GameState) -> None:
        super().__init__()

        # TODO: Player/CPU selection screen
        self.game = game

    def compose(self) -> ComposeResult:
        yield Header()
        with CenterMiddle():
            yield Chessboard().data_bind(Chessinator2000.game)
        with Center():
            yield Button(id="reset", label="Restart")

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.players = [
            Cpu(self, PieceColor.WHITE, RandomMover()),
            Cpu(self, PieceColor.BLACK, RandomMover()),
            # Player(self, PieceColor.BLACK),
        ]

        def start_game():
            self.mutate_reactive(Chessinator2000.game)

        self.set_timer(0.1, start_game)

    def on_button_pressed(self) -> None:
        self.game = DEFAULT_GAME

    def on_move_message(self, event: MoveMessage):
        self.game = event.move
