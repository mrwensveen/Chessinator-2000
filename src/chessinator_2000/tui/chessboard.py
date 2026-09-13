# pyright: reportCallIssue=false

from itertools import batched, chain

from rich.segment import Segment
from rich.style import Style
from textual.events import Click, MouseMove
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from chessinator_2000.gamestate import (
    GameState,
    Piece,
    PieceKind,
    Square,
    get_occupant,
)


class Chessboard(Widget):
    game: reactive[GameState | None] = reactive(None)
    hovered_square: reactive[Square | None] = reactive(None)
    selected_square: reactive[Square | None] = reactive(None)

    COMPONENT_CLASSES = {  # noqa: RUF012
        "chessboard--white-square",
        "chessboard--black-square",
    }

    DEFAULT_CSS = """
    Chessboard {
        width: 88;
        height: 40;
    }
    Chessboard .chessboard--white-square {
        background: #A5BAC9;
    }
    Chessboard .chessboard--black-square {
        background: #004578;
    }
    """

    def __init__(self):
        with open("pieces.txt", "r") as f:
            self.pieces = frozendict(
                zip(PieceKind._member_map_.values(), batched(f.read().splitlines(), 5))
            )
        super().__init__()

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        row_index = y // 5  # A chessboard square consists of 4 rows

        if row_index >= 8:  # Generate blank lines when we reach the end
            return Strip.blank(self.size.width)

        is_odd = row_index % 2  # Used to alternate the starting square on each row

        white = self.get_component_rich_style("chessboard--white-square")
        black = self.get_component_rich_style("chessboard--black-square")

        # Generate a list of segments with alternating black and white space characters
        pieces = [
            None
            if not self.game
            else get_occupant(self.game, (column + 1, 8 - row_index))
            for column in range(8)
        ]
        segments = chain.from_iterable(
            [Segment(" " * 11, bgcolor)]
            if piece is None or y % 5 in (0, 4)
            else self._render_piece_column(piece, square, y, bgcolor)
            for column, piece in enumerate(pieces)
            if (bgcolor := black if (column + is_odd) % 2 else white)
            and (square := (column + 1, 8 - row_index))
        )
        strip = Strip(segments, 8 * 11)
        return strip

    def on_mouse_move(self, event: MouseMove) -> None:
        self.hovered_square = self._square_at(event.x, event.y)

    def on_click(self, event: Click) -> None:
        square = self._square_at(event.x, event.y)
        if (
            self.game is not None
            and (piece := get_occupant(self.game, square)) is not None
            and self.game.turn == piece.color
        ):
            self.selected_square = square

    def watch_hovered_square(self, _: Square, new_square: Square) -> None:
        self.log(new_square)

    def _render_piece_column(
        self, piece: Piece, square: Square, line_y: int, bgcolor: Style
    ) -> list[Segment]:
        sq_y = line_y % 5
        # if sq_y in (0, 4):
        #     if self.hover_square == square:
        #         return [Segment(" " * 11, Style(bgcolor=piece.color.name))]
        #     else:
        #         return [Segment(" " * 11, bgcolor)]

        style = Style(
            color=piece.color.flipped().name,
            bgcolor="#808080"
            if self.game is not None
            and self.game.turn == piece.color
            and square in (self.hovered_square, self.selected_square)
            else piece.color.name,
        )

        segments = [
            Segment("   ", bgcolor),
            Segment(self.pieces[piece.kind][sq_y].ljust(8)[3:], style),
            Segment("   ", bgcolor),
        ]

        return segments

    def _square_at(self, x: int, y: int) -> Square:
        return (x // 11 + 1, 8 - y // 5)
