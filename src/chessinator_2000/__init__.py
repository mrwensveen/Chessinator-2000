import sys
from collections.abc import Generator

from chessinator_2000.db.game_db import record_game_result
from chessinator_2000.gamestate import PieceColor
from chessinator_2000.mover import DatabaseMover, RandomPieceMover
from chessinator_2000.parser import Game

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


def main() -> None:
    print("Hello from chessinator-2000!\n")

    game = DEFAULT_GAME
    print(game)

    # app = Chessinator2000(game)
    # app.run()

    movers = frozendict() | {
        PieceColor.WHITE: DatabaseMover(PieceColor.WHITE),
        PieceColor.BLACK: RandomPieceMover(),
    }

    for turn in turns():
        move, score = m if (m := movers[turn].move(game)) is not None else (None, 0.0)

        if move is None:
            print(game.status)
            break

        if score > 0.0:
            print(score, file=sys.stderr)

        print(move)
        game = move

    # Record game result
    winner = (
        None if game.status in ("in_progress", "stalemate") else game.turn.flipped()
    )
    if winner is not None:
        print(f"Winner: {winner.name}")
    record_game_result(game, winner)


def turns(max: int = 1600) -> Generator[PieceColor]:
    for _ in range(int(max / 2)):
        yield PieceColor.WHITE
        yield PieceColor.BLACK
