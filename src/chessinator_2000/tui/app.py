from textual.app import App, ComposeResult
from textual.containers import CenterMiddle, HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Button, Header

from chessinator_2000.gamestate import GameState, PieceColor, Square, get_previous_games
from chessinator_2000.parser import Game
from chessinator_2000.tui.chessboard import Chessboard
from chessinator_2000.tui.player import Player, PlayerChoicesChanged, PlayerMoved
from chessinator_2000.tui.screens.end import EndScreen
from chessinator_2000.tui.screens.start import StartScreen, StartScreenResult

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
    SCREENS = {"start": StartScreen}  # noqa: RUF012
    CSS_PATH = "app.tcss"

    game: reactive[GameState | None] = reactive(None)
    selected_square: reactive[Square | None] = reactive(None)
    choice_squares: reactive[frozenset[Square]] = reactive(frozenset())
    chosen_square: reactive[Square | None] = reactive(None)

    players: frozendict[PieceColor, object] = frozendict()
    allow_db: bool = False

    def __init__(self, game: GameState) -> None:
        super().__init__()
        self.set_reactive(Chessinator2000.game, game)

    def compose(self) -> ComposeResult:
        yield Header()
        with CenterMiddle():
            yield (
                Chessboard()
                .data_bind(Chessinator2000.game)
                .data_bind(Chessinator2000.selected_square)
                .data_bind(Chessinator2000.choice_squares)
            )
        with HorizontalGroup():
            yield Button("↶ Undo", id="undo", disabled=True)
            yield Button("Restart game", id="new_game")

    def on_mount(self) -> None:
        self.push_screen("start", self._start_game)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in ("undo", "new"):
            self.chosen_square = None
            self.selected_square = None
            self.choice_squares = frozenset()
            self.query_one(Chessboard).highlighted_squares = frozenset()

        if (
            event.button.id == "undo"
            and self.game is not None
            and self.game.previous is not None
        ):
            previous_player_game = next(
                (
                    p
                    for p in get_previous_games(self.game)
                    if isinstance(self.players[p.turn], Player)
                ),
                None,
            )
            if previous_player_game is not None:
                self.game = previous_player_game
        elif event.button.id == "new_game":
            self.game = DEFAULT_GAME
            self.query_one("#undo").disabled = True
            self.push_screen("start", self._start_game)

    def on_chessboard_square_selected(self, event: Chessboard.SquareSelected) -> None:
        if event.square == self.selected_square:
            self.selected_square = None
            self.choice_squares = frozenset()
        else:
            self.selected_square = event.square

    def on_chessboard_choice_selected(self, event: Chessboard.ChoiceSelected) -> None:
        self.log(
            f"on_chessboard_choice_selected, current: {self.chosen_square}, new: {event.square}"
        )
        self.chosen_square = event.square

    def on_player_moved(self, event: PlayerMoved) -> None:
        if event.move is None:
            self.push_screen(
                EndScreen(self.game),
                lambda _: self.push_screen("start", self._start_game),
            )
            return

        self._highlight_move(event)
        self.game = event.move

        self.chosen_square = None
        self.selected_square = None
        self.choice_squares = frozenset()

        self.query_one("#undo").disabled = (
            event.move is None or event.move.previous is None
        )

    def on_player_choices_changed(self, event: PlayerChoicesChanged) -> None:
        self.choice_squares = event.squares

    def _highlight_move(self, event: PlayerMoved) -> None:
        if self.game is not None and event.move is not None:
            game_squares = {
                square
                for square, piece in self.game.board.items()
                if piece.color == self.game.turn
            }
            move_squares = {
                square
                for square, piece in event.move.board.items()
                if piece.color == self.game.turn
            }

            src = next(iter(game_squares - move_squares), None)
            dst = next(iter(move_squares - game_squares), None)
            self.query_one(Chessboard).highlighted_squares = frozenset(
                sq for sq in (src, dst) if sq is not None
            )

    def _start_game(
        self,
        start: StartScreenResult | None,
    ) -> None:
        if start is None:
            self.push_screen("start", self._start_game)
            return

        self.players = frozendict() | {
            PieceColor.WHITE: start.player_white(self, PieceColor.WHITE),
            PieceColor.BLACK: start.player_black(self, PieceColor.BLACK),
        }
        self.allow_db = start.allow_db

        self.mutate_reactive(Chessinator2000.game)
