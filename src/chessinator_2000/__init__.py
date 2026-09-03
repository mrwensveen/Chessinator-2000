from chessinator_2000.gamestate import (
    GameState,
    Piece,
    PieceColor,
    PieceKind,
    get_attackers,
    get_possible_moves,
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

    board = frozendict() | {
        (5, 1): Piece(PieceColor.WHITE, PieceKind.KING),
        # (6, 1): Piece(PieceColor.WHITE, PieceKind.BISHOP),
        (8, 1): Piece(PieceColor.BLACK, PieceKind.ROOK),
    }

    game = GameState(board, PieceColor.WHITE)
    print(game)
    # print(get_attackers(game, (5, 2)))

    moves = get_possible_moves(game)
    for move in moves:
        print(move)
