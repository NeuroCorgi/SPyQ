from __future__ import annotations

from functools import wraps
from dataclasses import dataclass
from typing import (
    Callable,
    Iterator,
    Union,
)

def _binary_op(op: str) -> Callable[Callable[[Field, Any], Query], Callable[[Field, Any], Query]]:

    def decorator(bin_op: Callable[[Field, Any], Query]) -> Callable[[Field, Any], Query]:
        @wraps(bin_op)
        def wrapper(self: Field, other: Any) -> Query:
            bin_op(self, other)
            node = BinOp(self, op, other)
            query = Query(self.table.fields, self.table.from_list, node)

            # If a filter applied on a query with filters, both filters are used with `and` in between
            return query if not self.table.filter_tree else (query & self.table.filter_tree)

        return wrapper

    return decorator


class _Field:

    table: Query
    name: str

    def __init__(self, obj: Query, name: str):
        self.table = obj
        self.name = name

    @_binary_op("=")
    def __eq__(self, other: Any):
        # TODO: type checking
        if other is None:
            raise TypeError("None is not supported")

    @_binary_op("!=")
    def __ne__(self, other: Any): pass

    @_binary_op("CONTAINS")
    def __contains__(self, other: Any): pass

    @_binary_op(">")
    def __gt__(self, other: Any): pass

    @_binary_op(">=")
    def __ge__(self, other: Any): pass

    @_binary_op("<")
    def __lt__(self, other: Any): pass

    @_binary_op("<=")
    def __le__(self, other: Any): pass

    # def __and__(self, other: _Field):
    #     return Query(self.table.fields | other.table.fields

    def __iter__(self) -> Iterator:
        query = SelectQuery(Query(FieldList(self.name), self.table.from_list, self.table.filter_tree))
        sql = _compile(query)

        return iter(_spyq_conn.execute(sql).fetchall())

    def _set(self, val: Any):
        query = UpdateQuery(Query(FieldList(self.name), self.table.from_list, self.table.filter_tree), val)
        sql = _compile(query)

        _spyq_conn.execute(sql)
        _spyq_conn.commit()


class Field:

    name: str

    def __set_name__(self, _, name: str):
        self.name = name

    def __get__(self, obj: Query, cls=None):
        return _Field(obj, self.name)

    def __set__(self, obj: Query, val: Any):
        _Field(obj, self.name)._set(val)


@dataclass
class FieldList:

    fields: Union[str, set[str]]

    def __or__(self, other: FieldList) -> FieldList:
        return FieldList(set(self.fields) | set(other.fields))

    def __contains__(self, name: str)-> bool:
        if type(self.fields) is str:
            return self.fields == name
        return name in self.fields


class Query:

    fields: FieldList
    from_list: tuple[FromNode]   = ()
    filter_tree: Optional[BinOp] = None

    def __init__(self, fields: FieldList, from_list: tuple[FromNode], filter_tree: Optional[BinOp] = None):

        self.fields = fields
        self.from_list = from_list
        self.filter_tree = filter_tree

    def __and__(self, other: Query) -> Query:
        # TODO: assert equality of fields and from_list
        return Query(self.fields, self.from_list, BinOp(self.filter_tree, "AND", other.filter_tree))

    def __or__(self, other: Query) -> Query:
        return Query(self.fields, self.from_list, BinOp(self.filter_tree, "OR", other.filter_tree))

    def __repr__(self) -> str:
        return f"<SPyQ.Query: fields-{self.fields}, filter-{self.filter_tree}>"

    def __iter__(self) -> Iterator:
        query = SelectQuery(self)
        sql = _compile(query)

        return iter(_spyq_conn.execute(sql).fetchall())


@dataclass
class SelectQuery:
    query: Query


@dataclass
class UpdateQuery:
    query: Query
    value: Any
