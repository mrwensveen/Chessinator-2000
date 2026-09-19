from itertools import chain

from textual.app import App
from textual.message import Message

from chessinator_2000.gamestate import (
    GameState,
    PieceColor,
    Square,
    get_occupant,
    get_piece_moves,
)
from chessinator_2000.mover import Mover
from chessinator_2000.tui.chessboard import Chessboard


class PlayerMoved(Message):
    def __init__(self, move: GameState | None) -> None:
        super().__init__()
        self.move = move


class PlayerChoicesChanged(Message):
    def __init__(self, squares: frozenset[Square]) -> None:
        super().__init__()
        self.squares = squares


class Player:
    game: GameState | None = None
    selected_quare: Square | None = None
    choice_moves: tuple[GameState, ...] = ()

    def __init__(self, app: App, color: PieceColor):
        self.app = app
        self.color = color

        app.watch(app, "game", self.handle_update_game, init=False)
        app.watch(
            app, "selected_square", self.handle_update_selected_square, init=False
        )
        app.watch(app, "chosen_square", self.handle_update_chosen_square, init=False)

    def handle_update_game(self, game: GameState) -> None:
        # if game.turn == self.color:
        #     self.app.log(f"Player: {self.color}")

        self.game = game
        self.selected_quare = None

    def handle_update_selected_square(self, square: Square | None) -> None:
        if self.game is None or self.game.turn != self.color or square is None:
            return

        if (
            (game := self.game) is None
            or game.turn != self.color
            or (piece := get_occupant(game, square)) is None
        ):
            return

        self.selected_quare = square

        piece_moves = tuple(get_piece_moves(game, square, piece))
        self.choice_moves = piece_moves

        def _color_squares(g: GameState) -> set[Square]:
            return {s for s, p in g.board.items() if p.color == self.color}

        game_squares = _color_squares(game)
        choices = frozenset(
            chain.from_iterable(
                iter(_color_squares(move) - game_squares) for move in piece_moves
            )
        )
        self.app.post_message(PlayerChoicesChanged(choices))

    def handle_update_chosen_square(self, square: Square | None) -> None:
        if self.game is None or self.game.turn != self.color or square is None:
            return

        self.app.log(f"handle_update_chosen_square: {square}")
        if not self.choice_moves:
            return

        move = next(
            iter(
                move
                for move in self.choice_moves
                if (occupant := get_occupant(move, square)) is not None
                and occupant.color == self.color
            ),
            None,
        )
        self.app.post_message(PlayerMoved(move))


class Cpu:
    def __init__(self, app: App, color: PieceColor, mover: Mover):
        self.app = app
        self.color = color
        self.mover = mover

        app.watch(app, "game", self.handle_update_game, init=False)

    def handle_update_game(self, game: GameState) -> None:
        if game.turn != self.color:
            return

        # self.app.log(f"Cpu({type(self.mover).__name__}): {self.color}")

        def do_move():
            move = self.mover.move(game)
            if move is not None:
                game_squares = {
                    square
                    for square, piece in game.board.items()
                    if piece.color == self.color
                }
                move_squares = {
                    square
                    for square, piece in move.board.items()
                    if piece.color == self.color
                }
                if (src := next(iter(game_squares - move_squares), None)) is not None:
                    self.app.post_message(Chessboard.SquareSelected(src))

                if (dst := next(iter(move_squares - game_squares), None)) is not None:
                    self.app.post_message(Chessboard.ChoiceSelected(dst))

            self.app.post_message(PlayerMoved(move))

        self.app.set_timer(1, do_move)
