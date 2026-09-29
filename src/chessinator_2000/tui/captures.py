from collections import Counter

from textual.app import ComposeResult
from textual.coordinate import Coordinate
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable

from chessinator_2000.gamestate import GameState, PieceColor, PieceKind


class Captures(Widget):
    game: reactive[GameState | None] = reactive(None)
    captures: reactive[frozendict[PieceKind, int]] = reactive(frozendict())

    def __init__(self, start_game: GameState, color: PieceColor) -> None:
        self.color = color
        self.start_count = Counter(
            p.kind for _, p in start_game.board.items() if p.color == self.color
        )
        super().__init__()

    def on_mount(self) -> None:
        self.border_title = "Captures"
        table = self.query_one(DataTable)
        table.add_column("Piece", width=8)
        table.add_rows(("") for _ in PieceKind)

    def compute_captures(self) -> frozendict[PieceKind, int]:
        if self.game is None:
            return frozendict()

        current_count = Counter(
            p.kind for _, p in self.game.board.items() if p.color == self.color
        )
        captured = self.start_count - current_count
        return frozendict() | captured

    def watch_captures(self, captures: frozendict[PieceKind, int]) -> None:
        table = self.query_one(DataTable)
        for k, f in captures.items():
            table.update_cell_at(Coordinate(k.value - 1, 0), str(f))

    def compose(self) -> ComposeResult:
        yield DataTable()
