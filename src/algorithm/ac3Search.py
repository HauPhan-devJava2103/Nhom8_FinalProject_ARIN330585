import heapq
from collections import deque
from typing import Set, Optional, List, Tuple, Dict
from model.board import Board
from model.node import Node
from .exception import NoSolutionFoundException
from .result import Result


def ac3_search(board: Board, max_depth: int = 2000, max_frontier_size: int = 100000, verbose: bool = False) -> Result:
    """
    AC-3 cải tiến cho Rush Hour:
    - Chạy AC-3 propagation nhưng KHÔNG cắt nhánh nếu thất bại
    - Thay vào đó, tiếp tục với board gốc như thuật toán tìm kiếm thông thường
    - Ưu tiên các trạng thái đã được propagate thành công
    """

    def priority_of_board(b: Board) -> int:
        try:
            domains = b.get_all_domains()
            total = sum(len(domains[var]) for var in domains)
        except Exception:
            try:
                total = b.get_minimum_cost()
            except Exception:
                total = 0
        return total

    def try_ac3_propagation(source_board: Board) -> Optional[Board]:
        """
        Thử chạy AC-3 trên board.
        Trả về board đã propagate nếu thành công, None nếu thất bại.
        """
        def revise(consistent_board: Board, xi, xj) -> bool:
            revised = False
            domain_i = list(consistent_board.get_domain(xi))
            domain_j = list(consistent_board.get_domain(xj))

            new_domain_i = []
            for vi in domain_i:
                ok = False
                for vj in domain_j:
                    if consistent_board.is_consistent(xi, vi, xj, vj):
                        ok = True
                        break
                if ok:
                    new_domain_i.append(vi)

            if len(new_domain_i) < len(domain_i):
                consistent_board.set_domain(xi, new_domain_i)
                revised = True
            return revised

        try:
            consistent_board = source_board.copy()
            arcs = list(consistent_board.get_all_arcs())
            arcs_q = deque(arcs)

            while arcs_q:
                xi, xj = arcs_q.popleft()
                if revise(consistent_board, xi, xj):
                    # Nếu domain trống -> propagation thất bại
                    if len(consistent_board.get_domain(xi)) == 0:
                        return None
                    # Push neighbors
                    for xk in consistent_board.get_neighbors(xi):
                        if xk != xj:
                            arcs_q.append((xk, xi))
            
            return consistent_board
        except Exception:
            return None

    # Khởi tạo frontier
    frontier: List[Tuple[int, int, Node]] = []
    counter = 0

    start_node = Node(parent=None, board=board, depth=0, g_value=0, h_value=0)
    start_priority = priority_of_board(board)
    heapq.heappush(frontier, (start_priority, counter, start_node))
    counter += 1

    visited: Dict[Board, int] = {board: 0}
    explored_count = 0

    while frontier:
        if len(frontier) > max_frontier_size:
            if verbose:
                print("⚠️ Frontier vượt giới hạn, dừng sớm.")
            break

        _, _, node = heapq.heappop(frontier)
        explored_count += 1

        if verbose and explored_count % 1000 == 0:
            print(f"Explored: {explored_count}, frontier: {len(frontier)}")

        # Kiểm tra điều kiện đích
        if node.board.is_final_configuration():
            return Result(node=node, number_of_explored_states=explored_count, cost=node.g_value)

        if node.depth >= max_depth:
            continue

        # Thử AC-3 propagation
        propagated_board = try_ac3_propagation(node.board)
        
        # Nếu propagation thành công
        if propagated_board is not None:
            # Kiểm tra xem propagated board có phải là đích không
            if propagated_board.is_final_configuration():
                child_node = Node(parent=node, board=propagated_board, 
                                depth=node.depth + 1, g_value=node.g_value, h_value=0)
                return Result(node=child_node, number_of_explored_states=explored_count, 
                            cost=child_node.g_value)
            
            # Sử dụng propagated board để sinh moves
            working_board = propagated_board
            is_propagated = True
        else:
            # Nếu propagation thất bại, sử dụng board gốc
            working_board = node.board
            is_propagated = False
            if verbose and explored_count % 100 == 0:
                print(f"⚠️ AC-3 propagation thất bại, sử dụng board gốc")

        # Sinh các nước đi từ working_board
        try:
            moves = list(working_board.get_moves())
            candidate_boards = []
            
            for move, cost in moves:
                try:
                    new_board = working_board.move_vehicle(move)
                    candidate_boards.append((new_board, cost))
                except Exception:
                    continue
            
            # Ưu tiên board từ propagation thành công
            if is_propagated:
                candidate_boards.sort(key=lambda bc: priority_of_board(bc[0]))
            
            # Thêm vào frontier
            for new_board, move_cost in candidate_boards:
                new_depth = node.depth + 1
                
                # Kiểm tra visited
                best_seen = visited.get(new_board)
                if best_seen is not None and new_depth >= best_seen:
                    continue
                visited[new_board] = new_depth

                child = Node(
                    parent=node,
                    board=new_board,
                    depth=new_depth,
                    g_value=node.g_value + move_cost,
                    h_value=0
                )
                priority = priority_of_board(new_board)
                # Bonus: giảm priority nếu từ propagated board
                if is_propagated:
                    priority = priority * 0.9
                    
                heapq.heappush(frontier, (priority, counter, child))
                counter += 1
                
        except Exception as e:
            if verbose:
                print(f"Lỗi khi sinh moves: {e}")
            continue

    raise NoSolutionFoundException("Không tìm thấy lời giải sau khi duyệt hết không gian tìm kiếm.")