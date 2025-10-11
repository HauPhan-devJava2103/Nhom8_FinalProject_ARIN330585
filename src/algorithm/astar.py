import heapq
from typing import Dict, Set
from model.board import Board
from model.node import Node
from .exception import NoSolutionFoundException
from .result import Result


def a_star(board: Board, max_depth: int = 10000) -> Result:
    """
    Thuật toán A* cải tiến cho trò chơi Rush Hour.
    """

    open_list: list[tuple[int, Node]] = []
    visited: Dict[Board, int] = {}  # Lưu trạng thái kèm f_value tốt nhất đã thấy

    # Node bắt đầu
    start_node = Node(
        parent=None,
        board=board,
        g_value=0,
        h_value=board.get_minimum_cost()
    )

    heapq.heappush(open_list, (start_node.f_value, start_node))
    visited[board] = start_node.f_value

    explored_count = 0

    while open_list:
        _, current_node = heapq.heappop(open_list)
        explored_count += 1

        # Nếu là trạng thái đích
        if current_node.board.is_final_configuration():
            return Result(
                node=current_node,
                number_of_explored_states=explored_count,
                cost=current_node.g_value
            )

        # Tránh quá sâu
        if current_node.depth > max_depth:
            continue

        # Sinh các bước đi hợp lệ
        for move, move_cost in current_node.board.get_moves():
            new_board = current_node.board.move_vehicle(move)
            g = current_node.g_value + move_cost
            h = new_board.get_minimum_cost()
            f = g + h

            # Nếu trạng thái mới chưa thăm hoặc có f tốt hơn
            if new_board not in visited or f < visited[new_board]:
                child_node = Node(
                    parent=current_node,
                    board=new_board,
                    depth=current_node.depth + 1,
                    g_value=g,
                    h_value=h
                )
                heapq.heappush(open_list, (f, child_node))
                visited[new_board] = f

    # Nếu chạy hết mà chưa ra kết quả
    raise NoSolutionFoundException("Không tìm thấy lời giải — kiểm tra lại get_moves() hoặc heuristic.")
