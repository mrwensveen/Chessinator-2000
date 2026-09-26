# pyright: reportCallIssue=false

from itertools import batched, chain

from rich.segment import Segment
from rich.style import Style
from textual.events import MouseMove
from textual.message import Message
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from chessinator_2000.gamestate import (
    GameState,
    Piece,
    PieceColor,
    PieceKind,
    Square,
    get_occupant,
)


class Chessboard(Widget):
    COMPONENT_CLASSES = {  # noqa: RUF012
        "chessboard--white-square",
        "chessboard--black-square",
        "chessboard--action-square",
    }

    BINDINGS = [  # noqa: RUF012
        ("left", "move_hover((-1, 0))"),
        ("right", "move_hover((1, 0))"),
        ("up", "move_hover((0, 1))"),
        ("down", "move_hover((0, -1))"),
        ("space", "select()"),
        ("enter", "select()"),
    ]

    class SquareSelected(Message):
        def __init__(self, square: Square) -> None:
            super().__init__()
            self.square = square

    class ChoiceSelected(SquareSelected):
        def __init__(self, square: Square) -> None:
            super().__init__(square)

    game: reactive[GameState | None] = reactive(None)
    selected_square: reactive[Square | None] = reactive(None)
    choice_squares: reactive[frozenset[Square]] = reactive(frozenset())

    hovered_square: reactive[Square | None] = reactive(None)
    highlighted_squares: reactive[frozenset[Square]] = reactive(frozenset())

    def __init__(self):
        self.can_focus = True

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
            self._render_empty_square_line(square, y, bgcolor)
            if piece is None
            else self._render_piece_square_line(piece, square, y, bgcolor)
            for column, piece in enumerate(pieces)
            if (bgcolor := black if (column + is_odd) % 2 else white)
            and (square := (column + 1, 8 - row_index))
        )
        strip = Strip(segments, 8 * 11)
        return strip

    def on_mouse_move(self, event: MouseMove) -> None:
        self.hovered_square = self._square_at(event.x, event.y)

    def on_leave(self) -> None:
        self.hovered_square = None

    async def on_click(self) -> None:
        await self.run_action("select()")

    #         if self.game is None:
    #             return
    #
    #         square = self._square_at(event.x, event.y)
    #         if (
    #             piece := get_occupant(self.game, square)
    #         ) is not None and self.game.turn == piece.color:
    #             self.post_message(self.SquareSelected(square))
    #             return
    #
    #         if square in self.choice_squares:
    #             self.post_message(self.ChoiceSelected(square))
    #             return

    def _render_empty_square_line(
        self, square: Square, line_y: int, bgcolor: Style
    ) -> list[Segment]:
        action_square_style = self.get_component_rich_style("chessboard--action-square")

        inner_style = action_square_style if square in self.choice_squares else bgcolor

        sq_y = line_y % 5
        if sq_y in (0, 4):
            return self._render_top_bottom(square, bgcolor, action_square_style)

        return [
            Segment("   ", bgcolor),
            Segment("     ", inner_style),
            Segment("   ", bgcolor),
        ]

    def _render_piece_square_line(
        self, piece: Piece, square: Square, line_y: int, bgcolor: Style
    ) -> list[Segment]:
        action_square_style = self.get_component_rich_style("chessboard--action-square")

        sq_y = line_y % 5
        if sq_y in (0, 4):
            return self._render_top_bottom(square, bgcolor, action_square_style)

        bgcolor_piece = (
            action_square_style.bgcolor
            if self.game is not None
            and self.game.turn == piece.color
            and square in (self.hovered_square, self.selected_square)
            or square in self.choice_squares
            else piece.color.name
        )

        style = Style(
            color=piece.color.flipped().name,
            bgcolor=bgcolor_piece,
        )

        segments = [
            Segment("   ", bgcolor),
            Segment(self.pieces[piece.kind][sq_y].ljust(8)[3:], style),
            Segment("   ", bgcolor),
        ]

        return segments

    def _render_top_bottom(
        self, square: Square, bgcolor: Style, action_style: Style
    ) -> list[Segment]:
        return (
            [Segment(" " * 11, bgcolor)]
            if square not in self.highlighted_squares | {self.hovered_square}
            else [
                Segment(" ", action_style),
                Segment(" " * 9, bgcolor),
                Segment(" ", action_style),
            ]
        )

    def _square_at(self, x: int, y: int) -> Square:
        return (x // 11 + 1, 8 - y // 5)

    def action_move_hover(self, direction: Square) -> None:
        if (game := self.game) is None:
            return

        if self.hovered_square is None:
            self.hovered_square = (1, (1 if game.turn == PieceColor.WHITE else 8))
            return

        x, y = self.hovered_square
        dx, dy = direction
        self.hovered_square = _clamp((x + dx, y + dy))

    def action_select(self) -> None:
        if (game := self.game) is None:
            return
        if (square := self.hovered_square) is None:
            return

        if (
            piece := get_occupant(game, square)
        ) is not None and game.turn == piece.color:
            self.post_message(self.SquareSelected(square))
            return

        if square in self.choice_squares:
            self.post_message(self.ChoiceSelected(square))
            return

def _clamp(sq: Square) -> Square:
    x, y = sq
    return (min(max(x, 1), 8), min(max(y, 1), 8))
