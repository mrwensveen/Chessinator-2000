import random

from chessinator_2000.gamestate import get_possible_moves
from chessinator_2000.parser import Game

DEFAULT_GAME = Game("""
    |r᷺|n᷺|b᷺|q᷺|k᷺|b᷺|n᷺|r᷺|
    |p᷺|p᷺|p᷺|p᷺|p᷺|p᷺|p᷺|p᷺|
    | | | | | | | | |
    | | | | | | | | |
    | | | | | | | | |
    | | | | | | | | |
    |P᷺|P᷺|P᷺|P᷺|P᷺|P᷺|P᷺|P᷺|
    |R᷺|N᷺|B᷺|Q᷺|K᷺|B᷺|N᷺|R᷺|
    turn=WHITE
""")



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

    # game = DEFAULT_GAME
    game = Game("""
        | |n᷺|b᷺| |k᷺| | |r᷺|
        |r|p᷺| | |p᷺|p᷺| | |
        | | | | | |n| | |
        |p| | |p| | |p|P|
        |P|p| |q|P| | |Q|
        | | |N| | | | |P|
        | |b|P᷺|P᷺|N|P᷺| | |
        | | | | |K᷺|B᷺| |R᷺|
        turn=WHITE
    """)
    print(game)

    # moves = get_possible_moves(game)
    # for move in moves:
    #     print(move)

    # print(game.status)

    for _ in range(1):
        if len(game.board) == 2:
            break

        # try:
        #     moves = list(get_possible_moves(game))
        # except RecursionError as ex:
        #     print("ERROR", file=sys.stderr)
        #     print(game) ̲P̲P
        #     return

        moves = list(get_possible_moves(game))

        if len(moves) > 0:
            # Pick a random move
            game = random.choice(moves)
            print(game)
        else:
            break

    print(game.status)
