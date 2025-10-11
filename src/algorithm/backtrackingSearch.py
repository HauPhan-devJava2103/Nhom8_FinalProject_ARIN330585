from typing import Set, Optional, List
from model.board import Board
from model.node import Node
from .result import Result
from .exception import NoSolutionFoundException

def backtracking(board: Board, max_depth: int = 3000, keep_visited: bool = True) -> Result:
    """
    Backtracking với sắp xếp nước đi và debug.
    - keep_visited: Nếu True, giữ trạng thái trong visited. Nếu False, xóa khi quay lui.
    """
    visited: Set[Board] = set()

    h0 = board.get_minimum_cost()
    root = Node(board=board, depth=0, g_value=0, h_value=h0)

    if root.board.is_final_configuration():
        return Result(root, 1, root.g_value)

    def backtrack(node: Node) -> Optional[Result]:
        if node.depth >= max_depth:
            print(f"Stopped at depth {node.depth}, visited {len(visited)} states")
            return None

        moves = list(node.board.get_moves())
        print(f"Depth {node.depth}: {len(moves)} moves")
        moves.sort(key=lambda mv: node.board.move_vehicle(mv[0]).get_minimum_cost())

        for move, cost in moves:
            child_board = node.board.move_vehicle(move)
            if child_board in visited:
                continue
            visited.add(child_board)

            child = Node(
                parent=node,
                board=child_board,
                depth=node.depth + 1,
                g_value=node.g_value + cost,
                h_value=child_board.get_minimum_cost(),
            )

            if child.board.is_final_configuration():
                print(f"Solution found at depth {child.depth}, cost {child.g_value}")
                return Result(child, len(visited), child.g_value)

            result = backtrack(child)
            if result is not None:
                return result

            if not keep_visited:
                visited.remove(child_board)

        return None

    visited.add(root.board)
    result = backtrack(root)
    if result is None:
        print(f"No solution found, visited {len(visited)} states")
        raise NoSolutionFoundException()
    return result