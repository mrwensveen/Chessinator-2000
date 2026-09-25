from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, insert

from chessinator_2000 import DEFAULT_GAME

metadata_obj = MetaData()

game_result_table = Table(
    "game_results",
    metadata_obj,
    Column("game_state", String, primary_key=True),
    Column("white_wins", Integer),
    Column("black_wins", Integer),
    Column("num_played", Integer),
)


def main() -> None:
    engine = create_engine("sqlite+pysqlite:///c2k.db")
    metadata_obj.create_all(engine)
    stmt = insert(game_result_table).values(
        game_state=str(DEFAULT_GAME), white_wins=0, black_wins=0, num_played=1
    )
    print(stmt)
    with engine.begin() as conn:
        conn.execute(stmt)


if __name__ == "__main__":
    main()
