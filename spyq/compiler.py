from __future__ import annotations

from io import StringIO

from spyq.ast import (
    BinOp,
    FieldList,
    FieldNode,
    FromList,
    FromNode,
    FromNodeType,
    SelectQuery,
    UpdateQuery,
)


def _compile(obj) -> str:
    query = StringIO()
    match obj:
        # Simple values
        case int() | float() as num:
            query.write(f"{num}")
        case str() as string:
            query.write(f"{string!r}")
        case tuple() | list() | set() as values:
            query.write(f"{', '.join(map(str, values))}")

        # Fields
        case FieldList(fields=str() as field):
            query.write(field)
        case FieldList(fields=set() as fields):
            query.write(', '.join(fields))
        case FieldNode(name=name):
            # TODO: add table name
            query.write(name)

        # From
        case FromList(nodes=nodes):
            query.write(" ".join(map(_compile, nodes)))
        case FromNode(node_type=FromNodeType.SOURCE, table=str() as table):
            query.write(table)
        case FromNode(node_type=join, table=table, lhs_field=lhs, rhs_field=rhs):
            query.write(f"{join.value()} {table} ON {_compile(lhs)}={_compile(rhs)}")

        # Queries
        case SelectQuery(fields=fields, from_list=from_list, filter_tree=filter_tree):
            query.write(f"SELECT {_compile(fields)} FROM {_compile(from_list)} ")
            if filter_tree:
                query.write(" WHERE " + _compile(filter_tree))
        case UpdateQuery(fields=fields, from_list=from_list, filter_tree=filter_tree, value=val):
            query.write(f"UPDATE {_compile(from_list)} SET {_compile(fields)} = {_compile(val)}")
            if filter_tree:
                query.write(" WHERE " + _compile(filter_tree))

        # Filtering
        case BinOp(lhs=lhs, op=None, rhs=None):
            query.write(_compile(lhs))
        case BinOp(lhs=lhs, op=op, rhs=rhs):
            query.write(f"({_compile(lhs)}{op}{_compile(rhs)})")
            
        case _:
            raise ValueError(f"Unknown object to compile: {obj}")
    val = query.getvalue()
    print(val)
    return val
    return query.getvalue()
    
