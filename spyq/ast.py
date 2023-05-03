from __future__ import annotations

from dataclasses import dataclass

from enum import Enum, auto

from typing import (
    Any,
    Optional,
    Union,
    TypeAlias,
)


@dataclass
class SelectQuery:
    
    fields: FieldList
    from_list: FromList
    filter_tree: Optional[BinOp]


@dataclass
class UpdateQuery:
    
    fields: FieldList
    from_list: FromList
    filter_tree: Optional[BinOp]
    value: Any


@dataclass
class FieldNode:

    name: str


@dataclass
class FieldList:

    fields: Union[str, set[str]]

    def __or__(self, other: FieldList) -> FieldList:
        return FieldList(set(self.fields) | set(other.fields))

    def __contains__(self, name: str) -> bool:
        if type(self.fields) is str:
            return self.fields == name
        return name in self.fields


@dataclass
class BinOp:

    lhs: operand
    op:  Optional[str]
    rhs: Optional[operand]
    
operand: TypeAlias = Union[BinOp, FieldNode, SelectQuery]


class FromNodeType(Enum):

    SOURCE     = auto()
    INNER_JOIN = "INNER JOIN"
    LEFT_JOIN  = "LEFT JOIN"
    OUTER_JOIN = "JOIN"
    

@dataclass
class FromNode:
    
    node_type: FromNodeType
    table:     str
    lhs_field: Optional[str]
    rhs_field: Optional[str]


@dataclass
class FromList:

    nodes: tuple[FromNode]

    def __getitem__(self, index: int) -> FromNode:
        return self.nodes[index]
