from typing import Set, List
from model.board import Board
from model.node import Node
from .result import Result
from .exception import NoSolutionFoundException

def beam_search(board: Board, beam_width: int = 30, max_depth: int = 1000) -> Result:
    """
    Beam Search:
    - Mỗi tầng chỉ giữ lại 'beam_width' node có heuristic (h_value) nhỏ nhất.
    """
    visited: Set[Board] = set()

    # Node gốc
    h0 = board.get_minimum_cost()
    root = Node(board=board, depth=0, g_value=0, h_value=h0)

    # Kết quả từ nút gốc
    if root.board.is_final_configuration():
        return Result(root, 1, root.g_value)

    # Frontier tầng hiện tại
    current_layer: List[Node] = [root]
    visited.add(root.board)

    depth = 0
    while current_layer and depth < max_depth:
        depth += 1
        candidates: List[Node] = []

        # Sinh con cho tất cả node trong tầng
        for node in current_layer:
            if node.depth >= max_depth:
                continue

            for move, cost in node.board.get_moves():
                child_board = node.board.move_vehicle(move)

                if child_board in visited:
                    continue
                visited.add(child_board)

                g_child = node.g_value + cost
                h_child = child_board.get_minimum_cost()

                child = Node(
                    parent=node,
                    board=child_board,
                    depth=node.depth + 1,
                    g_value=g_child,
                    h_value=h_child,
                )

                # Nghiệm ngay khi sinh
                if child_board.is_final_configuration():
                    return Result(child, len(visited), child.g_value)

                candidates.append(child)

        # Chọn top-K theo h
        if not candidates:
            print(f"No candidates at depth {depth}. Visited states: {len(visited)}")
            break
        candidates.sort(key=lambda n: n.h_value)
        current_layer = candidates[:beam_width]

    raise NoSolutionFoundException()
