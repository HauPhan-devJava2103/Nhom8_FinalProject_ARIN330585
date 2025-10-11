from collections import deque
from typing import Set
from model.board import Board
from model.node import Node
from .exception import NoSolutionFoundException
from .result import Result


def breadth_first_search(board: Board, max_depth: int = 1000) -> Result:
    """
    Tìm kiếm theo chiều rộng (BFS) để giải bài toán Rush Hour.
    - board: trạng thái ban đầu
    - max_depth: độ sâu tối đa duyệt (phòng tránh lặp vô hạn)
    """

    # Hàng đợi FIFO lưu trữ các Node
    frontier = deque()
    root = Node(parent=None, board=board, depth=0, g_value=0, h_value=0)
    frontier.append(root)

    # Tập trạng thái đã duyệt để tránh lặp
    explored: Set[Board] = set()
    explored.add(board)

    number_of_explored_states = 0

    # Duyệt BFS
    while frontier:
        current_node = frontier.popleft()
        number_of_explored_states += 1

        # Kiểm tra trạng thái đích
        if current_node.board.is_final_configuration():
            return Result(
                node=current_node,
                number_of_explored_states=number_of_explored_states,
                cost=current_node.g_value
            )

        # Nếu quá sâu, bỏ qua
        if current_node.depth >= max_depth:
            continue

        # Sinh các nước đi hợp lệ
        for move, cost in current_node.board.get_moves():
            new_board = current_node.board.move_vehicle(move)

            # Nếu chưa từng duyệt
            if new_board not in explored:
                explored.add(new_board)
                child_node = Node(
                    parent=current_node,
                    board=new_board,
                    depth=current_node.depth + 1,
                    g_value=current_node.g_value + cost,
                    h_value=0  # BFS không dùng heuristic
                )
                frontier.append(child_node)

    # Nếu duyệt hết mà không có kết quả
    raise NoSolutionFoundException("Không tìm thấy lời giải trong giới hạn cho phép.")
