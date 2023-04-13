from __future__ import annotations

import sqlite3
from operator import itemgetter

from query import Query, Field


def discover(filename: str):
    global _spyq_conn
    _spyq_conn = sqlite3.connect(filename)

    tables: list[str] = conn.execute('SELECT name FROM sqlite_schema WHERE type="table" AND name NOT LIKE "sqlite_%";').fetchall()

    for table in tables:
        fields = tuple(map(
            itemgetter(0),
            conn.execute('SELECT name from PRAGMA_TABLE_INFO(?);', (table,))
                .fetchall()
        ))
        class_name = table.capitalize()
        globals()[class_name] = type(
            class_name,
            (Query,),
            {field: Field() for field in fields}
        )

