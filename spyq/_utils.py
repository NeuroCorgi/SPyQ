from __future__ import annotations

import sqlite3
from operator import itemgetter

from typing import Any

from spyq.ast import FromList, FromNode, FieldList, FromNodeType
from spyq.query import Query


def discover(filename: str, globals: dict[str, Any]):
    global _spyq_conn
    _spyq_conn = sqlite3.connect(filename)

    tables: map[str] = map(
        itemgetter(0),
        _spyq_conn.execute('SELECT name FROM sqlite_schema WHERE type="table" AND name NOT LIKE "sqlite_%";')
            .fetchall()
    )
    
    for table in tables:
        fields = tuple(map(
            itemgetter(0),
            _spyq_conn.execute('SELECT name from PRAGMA_TABLE_INFO(?);', (table,))
                .fetchall()
        ))
        class_name = table.capitalize()
        print(class_name)
        globals[class_name] = Query(FieldList(set(fields)), FromList((FromNode(FromNodeType.SOURCE, table, None, None),)))

    print(globals)

