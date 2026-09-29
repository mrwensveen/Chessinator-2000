from collections.abc import Iterable

from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
    select,
    update,
)

from chessinator_2000.gamestate import GameState, PieceColor, get_previous_games

metadata_obj = MetaData()

game_result_table = Table(
    "game_results",
    metadata_obj,
    Column("game_state", String, primary_key=True),
    Column("turn", Integer),
    Column("white_wins", Integer, default=0),
    Column("black_wins", Integer, default=0),
    Column("num_played", Integer, default=0),
)

engine = create_engine("sqlite+pysqlite:///c2k.db")
metadata_obj.create_all(engine)


def record_game_result(game: GameState, winner: PieceColor | None) -> None:
    games = {str(game): game.turn for game in (game, *get_previous_games(game))}

    with engine.begin() as conn:
        update_winners = (
            {}
            if winner is None
            else {"white_wins": game_result_table.c.white_wins + 1}
            if winner == PieceColor.WHITE
            else {"black_wins": game_result_table.c.black_wins + 1}
        )
        existing_states: set[str] = {
            state
            for (state,) in conn.execute(
                update(game_result_table)
                .where(game_result_table.c.game_state.in_(games.keys()))
                .values(
                    {"num_played": game_result_table.c.num_played + 1} | update_winners
                )
                .returning(game_result_table.c.game_state)
            )
        }

        new_states = {
            state: turn for state, turn in games.items() if state not in existing_states
        }
        if len(new_states) == 0:
            return

        insert_winners = (
            {"white_wins": 0, "black_wins": 0}
            if winner is None
            else {"white_wins": 1, "black_wins": 0}
            if winner == PieceColor.WHITE
            else {"white_wins": 0, "black_wins": 1}
        )
        conn.execute(
            insert(game_result_table),
            [
                {"game_state": state, "turn": turn.value, "num_played": 1}
                | insert_winners
                for state, turn in new_states.items()
            ],
        )


def find_game_results(
    turn: PieceColor, moves: Iterable[GameState]
) -> frozenset[tuple[str, int, int, int]]:
    games = {str(game) for game in moves}

    with engine.connect() as conn:
        found = conn.execute(
            select(game_result_table)
            .filter_by(turn=turn.value)
            .where(game_result_table.c.game_state.in_(games))
        )
        return frozenset(
            {
                (game_state, white_wins, black_wins, num_played)
                for game_state, _, white_wins, black_wins, num_played in found
            }
        )
