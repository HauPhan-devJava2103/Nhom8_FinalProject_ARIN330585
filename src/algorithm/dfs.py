from typing import Set, List
from model.board import Board
from model.node import Node
from .exception import NoSolutionFoundException
from .result import Result

def depth_first_search(board: Board, max_depth: int = 3000) -> Result:
    """
    DFS dạng lặp bằng stack (LIFO).
    - Tránh lặp trạng thái bằng visited (set các Board).
    """
    # Node gốc
    root = Node(parent = None,board=board, depth=0,g_value=0,h_value=0)       
    visited: Set[Board] = {board}           
    stack: List[Node] = [root]              

    # Nếu trạng thái gốc đã là đích
    if root.board.is_final_configuration():  
        return Result(
            node=root,
            number_of_explored_states=len(visited),
            cost=root.g_value
        )

    while stack:
        node = stack.pop()

        # Giới hạn độ sâu
        if node.depth >= max_depth:
            continue

        # Mở rộng các trạng thái con
        for move, cost in node.board.get_moves():
            child_board = node.board.move_vehicle(move)

            # Bỏ qua trạng thái đã thăm
            if child_board in visited:
                continue

            visited.add(child_board)
            child = Node(parent=node, board=child_board, depth=node.depth + 1,g_value=node.g_value + cost,h_value=0)

            # Kiểm tra nghiệm ngay khi sinh
            if child_board.is_final_configuration():
                return Result(child, len(visited),cost=child.g_value)

            # Thêm vào stack (LIFO)
            stack.append(child)

    # Hết stack mà chưa tìm thấy nghiệm
    raise NoSolutionFoundException()
