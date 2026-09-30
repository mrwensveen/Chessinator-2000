from textual.app import RenderResult
from textual.widget import Widget

from chessinator_2000.gamestate import PieceColor, PieceKind


class Piece(Widget):
    """A Piece Widget for in the Captures panel."""

    def __init__(self, kind: PieceKind, color: PieceColor) -> None:
        self.kind = kind
        self.color = color

        with open("pieces.txt", "r") as f:
            offset = 1 + (kind.value - 1) * 5
            self.piece = "\n".join(
                line[3:8] for line in f.read().splitlines()[offset : offset + 3]
            )

        super().__init__(classes=color.name.lower())

    def render(self) -> RenderResult:
        return self.piece
