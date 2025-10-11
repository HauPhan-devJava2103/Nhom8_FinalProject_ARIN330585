import heapq
from typing import Set, List
from model.board import Board
from model.node import Node
from .exception import NoSolutionFoundException
from .result import Result

def uniform_cost_search(board: Board, max_depth: int = 1000) -> Result:
    depth = 0
    visited_boards: Set[Board] = set()
    pq: List[Node] = []

    root = Node(board=board, depth=0, g_value=0)
    heapq.heappush(pq, root)
    visited_boards.add(root.board)

    if root.board.is_final_configuration():
        return Result(root, len(visited_boards))

    while pq and depth < max_depth:
        current_node = heapq.heappop(pq)
        depth = current_node.depth

        if current_node.board.is_final_configuration():
            return Result(current_node, len(visited_boards), current_node.g_value)

        for move, cost in current_node.board.get_moves():
            next_depth = current_node.depth + 1
            if next_depth > max_depth:
                continue

            child_board = current_node.board.move_vehicle(move=move)

            if child_board not in visited_boards:
                visited_boards.add(child_board)
                node = Node(
                    board=child_board,
                    parent=current_node,
                    depth=next_depth,
                    g_value=current_node.g_value + cost,
                )
                heapq.heappush(pq, node)

                if child_board.is_final_configuration():
                    return Result(node, len(visited_boards), node.g_value)

    raise NoSolutionFoundException()
