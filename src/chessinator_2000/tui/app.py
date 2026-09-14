from textual.app import App, ComposeResult
from textual.containers import Center, CenterMiddle
from textual.reactive import reactive
from textual.widgets import Button, Header

from chessinator_2000.gamestate import GameState, PieceColor, Square
from chessinator_2000.mover import FirstMover, RandomMover, RandomPieceMover
from chessinator_2000.parser import Game
from chessinator_2000.tui.chessboard import Chessboard
from chessinator_2000.tui.player import Cpu, Player, PlayerChoicesChanged, PlayerMoved

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
    selected_square: reactive[Square | None] = reactive(None)
    choice_squares: reactive[list[Square]] = reactive([])

    def __init__(self, game: GameState) -> None:
        super().__init__()

        # TODO: Player/CPU selection screen
        self.game = game

    def compose(self) -> ComposeResult:
        yield Header()
        with CenterMiddle():
            yield (
                Chessboard()
                .data_bind(Chessinator2000.game)
                .data_bind(Chessinator2000.selected_square)
                .data_bind(Chessinator2000.choice_squares)
            )
        with Center():
            yield Button(id="reset", label="Restart")

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.players: frozendict[PieceColor, object] = frozendict() | {
            PieceColor.WHITE: Cpu(self, PieceColor.WHITE, RandomPieceMover()),
            # PieceColor.BLACK: Cpu(self, PieceColor.BLACK, RandomMover()),
            PieceColor.BLACK: Player(self, PieceColor.BLACK),
        }

        def start_game():
            self.mutate_reactive(Chessinator2000.game)

        self.set_timer(0.1, start_game)

    def on_button_pressed(self) -> None:
        self.game = DEFAULT_GAME

    def on_chessboard_square_selected(self, event: Chessboard.SquareSelected) -> None:
        self.selected_square = event.square

    def on_player_moved(self, event: PlayerMoved) -> None:
        self.game = event.move
        self.selected_square = None

    def on_player_choices_changed(self, event: PlayerChoicesChanged) -> None:
        self.choice_squares = event.squares
