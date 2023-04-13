from __future__ import annotations

from io import StringIO
from dataclasses import dataclass

from typing import (
    Union,
    Optional
)


@dataclass
class BinOp:

    lhs: Union[BinOp, Any]
    op:  Optional[str]
    rhs: Optional[Union[BinOp, Any]]


def _compile(obj) -> str:
    query = StringIO()
    match obj:
        case int() | float() as num:
            query.write(f"{num}")
        case str() as string:
            query.write(f"{string!r}")
        case tuple() | list() | set() as values:
            query.write(f"{', '.join(map(str, values))}")
        case FieldList(fields=str() as field):
            query.write(field)
        case FieldList(fields=set() as fields):
            query.write(' '.join(fields))
        case SelectQuery(query=obj):
            query.write(f"SELECT {_compile(obj.fields)} FROM {_compile(obj.from_list)} ")
            if obj.filter_tree:
                query.write(" WHERE " + _compile(obj.filter_tree))
        case UpdateQuery(query=obj, value=val):
            query.write(f"UPDATE {_compile(obj.from_list)} SET {_compile(obj.fields)} = {_compile(val)}")
            if obj.filter_tree:
                query.write(" WHERE " + _compile(obj.filter_tree))
        case _Field(name=name):
            query.write(name)
        case BinOp(lhs=lhs, op=None, rhs=None):
            query.write(_compile(lhs))
        case BinOp(lhs=lhs, op=op, rhs=rhs):
            query.write(f"({_compile(lhs)}{op}{_compile(rhs)}")
        case _:
            raise ValueError(f"Unknown object to compile: {obj}")
    return query.getvalue()
    
