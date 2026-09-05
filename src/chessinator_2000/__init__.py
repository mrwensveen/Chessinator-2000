import random
import sys

from chessinator_2000.gamestate import Game, get_possible_moves

DEFAULT_GAME = Game(
    [
        "rnbqkbnr",
        "pppppppp",
        "",
        "",
        "",
        "",
        "PPPPPPPP",
        "RNBQKBNR",
    ]
)


def main() -> None:
    print("Hello from chessinator-2000!\n")

    # board = frozendict() | {
    #     (1, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
    #     (2, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
    #     (2, 4): Piece(PieceColor.BLACK, PieceKind.PAWN),
    # }

    # board = frozendict() | {
    #     (1, 3): Piece(PieceColor.WHITE, PieceKind.PAWN, moved=True),
    #     (2, 1): Piece(PieceColor.WHITE, PieceKind.KNIGHT),
    # }

    # board = frozendict() | {
    #     (1, 7): Piece(PieceColor.WHITE, PieceKind.PAWN, moved=True),
    #     (2, 8): Piece(PieceColor.BLACK, PieceKind.KNIGHT, moved=True),
    # }

    # board = frozendict() | {
    #     (1, 1): Piece(PieceColor.WHITE, PieceKind.ROOK),
    #     (5, 1): Piece(PieceColor.WHITE, PieceKind.KING),
    #     (8, 1): Piece(PieceColor.WHITE, PieceKind.ROOK),
    # }

    # board = frozendict() | {
    #     (4, 2): Piece(PieceColor.BLACK, PieceKind.PAWN),
    #     (4, 1): Piece(PieceColor.WHITE, PieceKind.QUEEN),
    # }

    # board = frozendict() | {
    #     (4, 2): Piece(PieceColor.BLACK, PieceKind.PAWN),
    #     (4, 3): Piece(PieceColor.BLACK, PieceKind.PAWN),
    #     (4, 1): Piece(PieceColor.WHITE, PieceKind.ROOK),
    #     (6, 1): Piece(PieceColor.WHITE, PieceKind.BISHOP),
    # }

    # game = GameState(board, PieceColor.WHITE)
    # print(game)

    # moves = get_possible_moves(game)
    # for move in moves:
    #     print(move)

    # board = frozendict() | {
    #     (4, 3): Piece(PieceColor.BLACK, PieceKind.PAWN),
    #     (4, 1): Piece(PieceColor.WHITE, PieceKind.ROOK),
    #     (6, 1): Piece(PieceColor.WHITE, PieceKind.BISHOP),
    # }

    # game = GameState(board, PieceColor.WHITE)
    # print(game)
    # print(get_attackers(game, (4, 3)))

    # board = frozendict() | {
    #     (5, 1): Piece(PieceColor.WHITE, PieceKind.KING),
    #     (8, 1): Piece(PieceColor.BLACK, PieceKind.ROOK),
    # }

    # board = frozendict() | {
    #     (5, 1): Piece(PieceColor.WHITE, PieceKind.KING),
    #     (8, 1): Piece(PieceColor.WHITE, PieceKind.ROOK),
    #     (5, 4): Piece(PieceColor.BLACK, PieceKind.QUEEN),
    # }

    # board = frozendict() | {
    #     P("f5"): Piece(PieceColor.WHITE, PieceKind.KING),
    #     P("h1"): Piece(PieceColor.WHITE, PieceKind.ROOK),
    #     P("h5"): Piece(PieceColor.BLACK, PieceKind.KING),
    # }

    # board = frozendict() | {
    #     Sq("a1"): Pc("K", moved=False),
    #     Sq("g6"): Pc("Q", moved=True),
    #     Sq("h8"): Pc("k", moved=False),
    # }

    # game = GameState(board, PieceColor.BLACK)

    game = DEFAULT_GAME
    # game = Game(
    #     [
    #         "r  qk nr",
    #         "  p",
    #         "ppnpb pb",
    #         "P   pp p",
    #         "   Q PPP",
    #         "R P  N",
    #         " P PP B",
    #         " NB K  R",
    #     ]
    # )
    print(game)

    # moves = get_possible_moves(game)
    # for move in moves:
    #     print(move)

    # print(game.status)

    for _ in range(750):
        if len(game.board) == 2:
            break

        try:
            moves = list(get_possible_moves(game))
        except RecursionError as ex:
            print("ERROR", file=sys.stderr)
            print(game)
            return

        if len(moves) > 0:
            # Pick a random move
            game = random.choice(moves)
            print(game)
        else:
            break

    print(game.status)
