from __future__ import annotations
from dataclasses import dataclass, field
from .board import Board
from typing import FrozenSet


@dataclass(frozen=True)
class Node:
    parent: Node | None = None
    board: Board = field(default=Board())
    belief: FrozenSet[Board] | None = field(default=None)
    depth: int = 0
    g_value: int = 0 
    h_value: int = 0 

    @property
    def f_value(self) -> int:
        return self.g_value + self.h_value

    def __le__(self, other):
        return self.f_value <= other.f_value

    def __lt__(self, other):
        return self.f_value < other.f_value


def get_history(node: Node) -> list[list]:
    board_history: list[list] = []
    current_node = node

    while current_node:
        board = current_node.board
        if board is None and current_node.belief:
            board = next(iter(current_node.belief))
        cost = current_node.g_value
        board_history.insert(0, [board, cost])
        current_node = current_node.parent

    return board_history