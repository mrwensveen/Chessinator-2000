from collections import Counter
from itertools import chain

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Digits

from chessinator_2000.gamestate import GameState, PieceColor, PieceKind
from chessinator_2000.tui.piece import Piece


class Captures(Widget):
    game: reactive[GameState | None] = reactive(None, recompose=True)
    captures: reactive[frozendict[PieceKind, int]] = reactive(frozendict())

    def __init__(self, start_game: GameState, color: PieceColor) -> None:
        self.color = color
        self.start_count = Counter(
            p.kind for _, p in start_game.board.items() if p.color == self.color
        )
        super().__init__(classes=color.name.lower())

    def compute_captures(self) -> frozendict[PieceKind, int]:
        if self.game is None:
            return frozendict()

        current_count = Counter(
            p.kind for _, p in self.game.board.items() if p.color == self.color
        )
        captured = self.start_count - current_count
        return frozendict() | captured

    def compose(self) -> ComposeResult:
        kinds = (
            iter(PieceKind) if self.color == PieceColor.WHITE else reversed(PieceKind)
        )
        yield from chain.from_iterable(
            (Piece(k, self.color), Digits(f"{f}"))
            for k in kinds
            if (f := self.captures.get(k, 0)) > 0
        )
