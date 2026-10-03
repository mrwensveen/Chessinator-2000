import argparse
import sys
from collections.abc import Generator

from chessinator_2000.db.game_db import record_game_result
from chessinator_2000.gamestate import GameState, PieceColor
from chessinator_2000.mover import DatabaseMover, RandomPieceMover
from chessinator_2000.parser import Game
from chessinator_2000.tui.app import Chessinator2000

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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-tui",
        action="store_true",
        help="Run without TUI. This starts a game between DatabaseMover and RandomPieceMover.",
    )
    args = parser.parse_args()

    game = DEFAULT_GAME

    if args.no_tui:
        run(game)
    else:
        app = Chessinator2000(game)
        app.run()


def run(game: GameState) -> None:
    print(game)

    movers = frozendict() | {
        PieceColor.WHITE: DatabaseMover(PieceColor.WHITE),
        PieceColor.BLACK: RandomPieceMover(),
    }

    n = 1
    for turn in turns():
        move, score = m if (m := movers[turn].move(game)) is not None else (None, 0.0)

        if move is None:
            print(f"{n:0>4}\t{game.status}")
            break

        if score != 0.0:
            print(f"{n:0>4}\t{score}", file=sys.stderr)

        print(move)
        game = move
        n += 1

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
