import heapq
from typing import Set, List, Tuple
from model.board import Board
from model.node import Node
from .exception import NoSolutionFoundException
from .result import Result

def greedy_search(board: Board, max_depth: int = 1000) -> Result:
    """
    Greedy Best-First Search: Ưu tiên theo h (heuristic)
    """
    visited: Set[Board] = set()
    pq: List[Tuple[int, int, Node]] = []   # (h, tie, node)
    tie = 0

    h0 = board.get_minimum_cost()
    root = Node(board=board, depth=0, g_value=0, h_value=h0)

    if root.board.is_final_configuration():
        return Result(root, 1, root.g_value)

    heapq.heappush(pq, (root.h_value, tie, root))
    visited.add(root.board)

    while pq:
        _, _, current = heapq.heappop(pq)

        if current.depth >= max_depth:
            continue

        if current.board.is_final_configuration():
            return Result(current, len(visited), current.g_value)

        for move, cost in current.board.get_moves():
            next_depth = current.depth + 1
            if next_depth > max_depth:
                continue

            child_board = current.board.move_vehicle(move)
            if child_board in visited:
                continue
            visited.add(child_board)

            g_child = current.g_value + cost  # chỉ để hiển thị/thống kê
            h_child = child_board.get_minimum_cost()

            child = Node(
                parent=current,
                board=child_board,
                depth=next_depth,
                g_value=g_child,
                h_value=h_child,
            )

            if child_board.is_final_configuration():
                return Result(child, len(visited), child.g_value)

            tie += 1
            heapq.heappush(pq, (h_child, tie, child))

    raise NoSolutionFoundException()
