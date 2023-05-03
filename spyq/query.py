from __future__ import annotations

from functools import wraps
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Iterator,
    Optional
)

from spyq.ast import (
    BinOp,
    FieldNode,
    FromList,
    FromNode,
    FieldList,
    SelectQuery,
    UpdateQuery
)

from spyq.compiler import _compile


def _binary_op(op: str) -> Callable[[Callable[[Field, Any], None]], Callable[[Field, Any], Query]]:

    def decorator(bin_op: Callable[[Field, Any], None]) -> Callable[[Field, Any], Query]:
        @wraps(bin_op)
        def wrapper(self: Field, other: Any) -> Query:
            bin_op(self, other)
            # TODO: add table name
            node = BinOp(FieldNode(self.name), op, other)
            query = Query(self.table._fields, self.table._from_list, node)

            # If a filter applied on a query with filters, both filters are used with `and` in between
            return query if not self.table._filter_tree else (query & self.table)

        return wrapper

    return decorator


class Field:

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

    def __iter__(self) -> Iterator:
        global _spyq_conn
        
        query = SelectQuery(FieldList(self.name), self.table._from_list, self.table._filter_tree)
        sql = _compile(query)

        return iter(_spyq_conn.execute(sql).fetchall())

    def _set(self, val: Any):
        global _spyq_conn
        
        query = UpdateQuery(FieldList(self.name), self.table._from_list, self.table._filter_tree, val)
        sql = _compile(query)

        _spyq_conn.execute(sql)
        _spyq_conn.commit()


class Query:
    
    _fields:      FieldList
    _from_list:   FromList
    _filter_tree: Optional[BinOp]

    def __init__(self, fields: FieldList, from_list: FromList, filter_tree: Optional[BinOp] = None):

        self._fields      = fields
        self._from_list   = from_list
        self._filter_tree = filter_tree

    def __getattr__(self, field: str):
        if field in self._fields:
            return Field(self, field)
        
        raise AttributeError(f'no field named "{field}" in the table "{self._from_list}"')

    def __setattr__(self, field: str, value: Any):
        if not field.startswith("_") and field in self._fields:
            return Field(self, field)._set(value)
        
        super(Query, self).__setattr__(field, value)

    def __and__(self, other: Query) -> Query:
        # TODO: assert equality of fields and from_list
        if self._filter_tree:
            return Query(self._fields, self._from_list, BinOp(self._filter_tree, "AND", other._filter_tree))
        return Query(self._fields, self._from_list, other._filter_tree)

    def __or__(self, other: Query) -> Query:
        if self._filter_tree:
            return Query(self._fields, self._from_list, BinOp(self._filter_tree, "OR", other._filter_tree))
        return Query(self._fields, self._from_list, other._filter_tree)

    def __repr__(self) -> str:
        return f"<SPyQ.Query: fields={self._fields}, filter={self._filter_tree}>"

    def __iter__(self) -> Iterator:
        global _spyq_conn
        
        query = SelectQuery(self._fields, self._from_list, self._filter_tree)
        sql = _compile(query)

        return iter(_spyq_conn.execute(sql).fetchall())

