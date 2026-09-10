# pyright: reportCallIssue=false

from itertools import batched, chain

from rich.segment import Segment
from rich.style import Style
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from chessinator_2000.gamestate import (
    GameState,
    Piece,
    PieceKind,
    get_occupant,
)


class Chessboard(Widget):
    game: reactive[GameState | None] = reactive(None)

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
            else self._render_piece_column(piece, bgcolor, y)
            for column, piece in enumerate(pieces)
            if (bgcolor := black if (column + is_odd) % 2 else white)
        )
        strip = Strip(segments, 8 * 11)
        return strip

    def _render_piece_column(
        self, piece: Piece, bgcolor: Style, y: int
    ) -> list[Segment]:
        return [
            Segment("   ", bgcolor),
            Segment(
                self.pieces[piece.kind][y % 5].ljust(8)[3:],
                Style.combine(
                    [
                        bgcolor,
                        Style(
                            color=piece.color.flipped().name,
                            bgcolor=piece.color.name,
                        ),
                    ]
                ),
            ),
            Segment("   ", bgcolor),
        ]
