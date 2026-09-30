from typing import cast

from textual.app import App, ComposeResult
from textual.containers import (
    CenterMiddle,
    Container,
    Horizontal,
    HorizontalGroup,
)
from textual.reactive import reactive
from textual.widgets import Button, Header, RichLog

from chessinator_2000.db.game_db import record_game_result
from chessinator_2000.gamestate import GameState, PieceColor, Square, get_previous_games
from chessinator_2000.tui.captures import Captures
from chessinator_2000.tui.chessboard import Chessboard
from chessinator_2000.tui.player import (
    CpuPlayer,
    Player,
    PlayerChoicesChanged,
    PlayerMoved,
    UserPlayer,
)
from chessinator_2000.tui.screens.end import EndScreen
from chessinator_2000.tui.screens.start import StartScreen, StartScreenResult


class Chessinator2000(App):
    TITLE = "Chessinator 2000!"
    SCREENS = {"start": StartScreen}  # noqa: RUF012
    CSS_PATH = "app.tcss"

    game: reactive[GameState | None] = reactive(None)
    selected_square: reactive[Square | None] = reactive(None)
    choice_squares: reactive[frozenset[Square]] = reactive(frozenset())
    chosen_square: reactive[Square | None] = reactive(None)

    players: frozendict[PieceColor, Player] = frozendict()
    allow_db: bool = False

    def __init__(self, game: GameState) -> None:
        super().__init__()

        self.start_game = game
        self.set_reactive(Chessinator2000.game, game)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Container(id="captures"):
                yield Captures(self.start_game, PieceColor.WHITE).data_bind(
                    Chessinator2000.game
                )
                yield Captures(self.start_game, PieceColor.BLACK).data_bind(
                    Chessinator2000.game
                )
            with CenterMiddle():
                yield (
                    Chessboard()
                    .data_bind(Chessinator2000.game)
                    .data_bind(Chessinator2000.selected_square)
                    .data_bind(Chessinator2000.choice_squares)
                )
            yield RichLog(wrap=True)
        with HorizontalGroup():
            yield Button("↶ Undo", id="undo", disabled=True)
            yield Button("Restart game", id="new_game")

    def watch_game(self, game: GameState | None) -> None:
        self.query_one("#undo").disabled = (
            game is None
            or game.previous is None
            or all(isinstance(p, CpuPlayer) for p in self.players.values())
        )

        if (
            game is not None
            and (player := self.players.get(game.turn, None)) is not None
        ):
            player.handle_update_game(game)

    def watch_selected_square(self, square: Square | None) -> None:
        if (
            self.game is not None
            and (player := self.players.get(self.game.turn, None)) is not None
        ):
            player.handle_update_selected_square(square)

    def watch_chosen_square(self, square: Square | None) -> None:
        if (
            self.game is not None
            and (player := self.players.get(self.game.turn, None)) is not None
        ):
            player.handle_update_chosen_square(square)

    def on_mount(self) -> None:
        self.push_screen("start", self._start_game)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in ("undo", "new_game"):
            self._reset_squares()

        if (
            event.button.id == "undo"
            and self.game is not None
            and self.game.previous is not None
        ):
            previous_player_game = next(
                (
                    p
                    for p in get_previous_games(self.game)
                    if isinstance(self.players[p.turn], UserPlayer)
                ),
                None,
            )
            if previous_player_game is not None:
                self.game = previous_player_game
        elif event.button.id == "new_game":
            self.players = frozendict()
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
        # TODO: Algebraic notation / PGN
        if event.message is not None:
            self.query_one(RichLog).write(event.message)

        if event.move is None:
            # Record this game in the database
            if self.allow_db and self.game is not None:
                winner = (
                    None
                    if self.game is None
                    or self.game.status in ("in_progress", "stalemate")
                    else self.game.turn.flipped()
                )

                record_game_result(self.game, winner)

            self.push_screen(
                EndScreen(self.game),
                lambda _: self.push_screen("start", self._start_game),
            )
            return

        self._reset_squares()
        self._highlight_move(event)
        self.game = event.move

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

    def _reset_squares(self) -> None:
        self.chosen_square = None
        self.selected_square = None
        self.choice_squares = frozenset()
        self.query_one(Chessboard).highlighted_squares = frozenset()

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
        if all(isinstance(p, CpuPlayer) for p in self.players.values()):
            for p in self.players.values():
                cast(CpuPlayer, p).delay = 0.1

        self.allow_db = start.allow_db

        self._reset_squares()
        self.query_one(RichLog).clear()

        self.set_reactive(Chessinator2000.game, self.start_game)
        self.mutate_reactive(Chessinator2000.game)
