from chessinator_2000.gamestate import (
    GameState,
    Piece,
    PieceColor,
    PieceKind,
    get_possible_moves,
)

DEFAULT_GAME = GameState(
    board=frozendict()
    | {
        (1, 8): Piece(PieceColor.BLACK, PieceKind.ROOK),
        (2, 8): Piece(PieceColor.BLACK, PieceKind.KNIGHT),
        (3, 8): Piece(PieceColor.BLACK, PieceKind.BISHOP),
        (4, 8): Piece(PieceColor.BLACK, PieceKind.KING),
        (5, 8): Piece(PieceColor.BLACK, PieceKind.QUEEN),
        (6, 8): Piece(PieceColor.BLACK, PieceKind.BISHOP),
        (7, 8): Piece(PieceColor.BLACK, PieceKind.KNIGHT),
        (8, 8): Piece(PieceColor.BLACK, PieceKind.ROOK),
        (1, 7): Piece(PieceColor.BLACK, PieceKind.PAWN),
        (2, 7): Piece(PieceColor.BLACK, PieceKind.PAWN),
        (3, 7): Piece(PieceColor.BLACK, PieceKind.PAWN),
        (4, 7): Piece(PieceColor.BLACK, PieceKind.PAWN),
        (5, 7): Piece(PieceColor.BLACK, PieceKind.PAWN),
        (6, 7): Piece(PieceColor.BLACK, PieceKind.PAWN),
        (7, 7): Piece(PieceColor.BLACK, PieceKind.PAWN),
        (8, 7): Piece(PieceColor.BLACK, PieceKind.PAWN),
        (1, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (2, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (3, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (4, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (5, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (6, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (7, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (8, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (1, 1): Piece(PieceColor.WHITE, PieceKind.ROOK),
        (2, 1): Piece(PieceColor.WHITE, PieceKind.KNIGHT),
        (3, 1): Piece(PieceColor.WHITE, PieceKind.BISHOP),
        (4, 1): Piece(PieceColor.WHITE, PieceKind.KING),
        (5, 1): Piece(PieceColor.WHITE, PieceKind.QUEEN),
        (6, 1): Piece(PieceColor.WHITE, PieceKind.BISHOP),
        (7, 1): Piece(PieceColor.WHITE, PieceKind.KNIGHT),
        (8, 1): Piece(PieceColor.WHITE, PieceKind.ROOK),
    },
    turn=PieceColor.WHITE,
)


def main() -> None:
    print("Hello from chessinator-2000!\n")

    board = frozendict() | {
        (1, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (2, 2): Piece(PieceColor.WHITE, PieceKind.PAWN),
        (2, 4): Piece(PieceColor.BLACK, PieceKind.PAWN),
    }

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

    # game = GameState(board, PieceColor.WHITE)
    game = DEFAULT_GAME
    print(game)

    moves = get_possible_moves(game)
    for move in moves:
        print(move)
