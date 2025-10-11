from typing import Dict, Set, Optional
from model.board import Board
from model.node import Node
from .exception import NoSolutionFoundException
from .result import Result


def And_Or_Search(board: Board, max_depth: int = 10000) -> Result:
    """
    Thuật toán AND–OR Search cho trò chơi Rush Hour.
    Dạng tổng quát: tìm chiến lược đạt đích trong không gian có thể phân nhánh.
    Trong Rush Hour, mỗi hành động cho ra 1 trạng thái nên cây AND có thể rút gọn.
    """

    explored_count = 0
    visited: Set[Board] = set()

    def or_search(state: Board, depth: int, parent: Optional[Node]) -> Optional[Node]:
        nonlocal explored_count

        explored_count += 1

        # Nếu đạt đích
        if state.is_final_configuration():
            return Node(parent=parent, board=state, depth=depth)

        # Giới hạn độ sâu
        if depth > max_depth:
            return None

        visited.add(state)

        # Sinh nước đi
        for move, cost in state.get_moves():
            new_board = state.move_vehicle(move)

            if new_board in visited:
                continue

            child = or_search(new_board, depth + 1, Node(parent, state, depth))
            if child is not None:
                return child  # Đã tìm thấy đường đi

        return None

    root_node = or_search(board, 0, None)

    if root_node is None:
        raise NoSolutionFoundException("Không tìm thấy lời giải bằng AND–OR Search.")
    else:
        return Result(
            node=root_node,
            number_of_explored_states=explored_count,
            cost=root_node.depth
        )
