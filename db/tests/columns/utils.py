from sqlalchemy import (
    CHAR, String, Integer, Boolean, select, Table, MetaData
)

from db.types import interval

column_test_dict = {
    Integer: {"start": "0", "set": "5", "expt": 5},
    String: {"start": "default", "set": "test", "expt": "test"},
    Boolean: {"start": "false", "set": "true", "expt": True},
    CHAR: {"start": "a", "set": "b", "expt": "b"},
    interval.Interval: {"start": "P1Y1M1DT1H1M1.1S", "set": "P1Y1M1DT2H1M1.2S", "expt": "P1Y1M1DT2H1M1.2S"}

}


def create_test_table(table_name, cols, insert_data, schema, engine):
    table = Table(
        table_name,
        MetaData(bind=engine, schema=schema),
        *cols
    )
    table.create()
    with engine.begin() as conn:
        for data in insert_data:
            conn.execute(table.insert().values(data))
    return table


def get_default(engine, table):
    with engine.begin() as conn:
        conn.execute(table.insert())
        return conn.execute(select(table)).fetchall()[0][0]
