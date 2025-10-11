from typing import Set, List, Tuple
import random
from model.board import Board
from model.node import Node
from .exception import NoSolutionFoundException
from .result import Result


def heuristic(board: Board) -> int:
    """Heuristic cơ bản: số ô cách cửa thoát của xe 0."""
    return board.get_minimum_cost()


def hill_climbing_search(board: Board, max_iterations: int = 10000, max_sideways: int = 100, verbose: bool = False) -> Result:
    """
    Hill Climbing cải tiến với nhiều chiến lược thoát local optimum:
    1. Random restart khi bị kẹt
    2. Chấp nhận tạm thời nước đi tệ hơn (simulated annealing style)
    3. Backtracking khi không còn đường đi
    4. Kết hợp best-first khi cần thiết
    """

    def explore_from_state(start_board: Board, start_node: Node, 
                          explored_global: Set[Board], iter_budget: int) -> Tuple[Node, int]:
        """
        Explore từ một trạng thái cho đến khi tìm được lời giải hoặc bị kẹt.
        Trả về (best_node_found, states_explored)
        """
        current_node = start_node
        explored_local = set()
        explored_local.add(start_board)
        sideways_moves = 0
        states_explored = 0
        
        for _ in range(iter_budget):
            if current_node.board.is_final_configuration():
                return current_node, states_explored

            neighbors = []
            for move, cost in current_node.board.get_moves():
                try:
                    new_board = current_node.board.move_vehicle(move)
                    # Cho phép revisit trong global nếu đạt được từ path khác
                    if new_board in explored_local:
                        continue
                    explored_local.add(new_board)
                    explored_global.add(new_board)
                    h_val = heuristic(new_board)
                    neighbors.append((h_val, move, cost, new_board))
                    states_explored += 1
                except Exception:
                    continue

            if not neighbors:
                break

            # Sắp xếp theo heuristic
            neighbors.sort(key=lambda x: x[0])
            
            # Lấy nhóm tốt nhất
            min_h = neighbors[0][0]
            best_neighbors = [n for n in neighbors if n[0] == min_h]
            h_val, move, cost, new_board = random.choice(best_neighbors)

            if h_val < current_node.h_value:
                # Cải thiện
                current_node = Node(current_node, new_board, current_node.depth + 1, 
                                   current_node.g_value + cost, h_val)
                sideways_moves = 0
            elif h_val == current_node.h_value and sideways_moves < max_sideways:
                # Sideways move
                sideways_moves += 1
                current_node = Node(current_node, new_board, current_node.depth + 1, 
                                   current_node.g_value + cost, h_val)
            else:
                # Bị kẹt - thử accept một nước đi tệ hơn với xác suất
                if len(neighbors) > 1 and random.random() < 0.3:  # 30% cơ hội
                    # Chọn nước đi tệ hơn nhưng không quá tệ
                    acceptable = [n for n in neighbors if n[0] <= current_node.h_value + 3]
                    if acceptable:
                        h_val, move, cost, new_board = random.choice(acceptable)
                        current_node = Node(current_node, new_board, current_node.depth + 1, 
                                           current_node.g_value + cost, h_val)
                        sideways_moves = 0
                        continue
                break

        return current_node, states_explored

    # Khởi tạo
    explored_global: Set[Board] = set()
    total_explored = 0
    best_node_overall = None
    best_h_overall = float('inf')
    
    max_restarts = 5
    restart_count = 0
    
    if verbose:
        print(f"🚀 Bắt đầu Hill Climbing với random restart")
        print(f"   Heuristic ban đầu: {heuristic(board)}")

    # Lần chạy đầu tiên từ trạng thái ban đầu
    start_node = Node(parent=None, board=board, depth=0, g_value=0, h_value=heuristic(board))
    result_node, explored = explore_from_state(board, start_node, explored_global, max_iterations)
    total_explored += explored
    
    if result_node.board.is_final_configuration():
        if verbose:
            print(f"✅ Tìm thấy lời giải ngay lần đầu!")
        return Result(result_node, total_explored, result_node.g_value)
    
    best_node_overall = result_node
    best_h_overall = result_node.h_value
    
    if verbose:
        print(f"   Lần 1: Kẹt tại h={result_node.h_value}, explored={explored}")

    # Random restart strategy
    while restart_count < max_restarts and total_explored < max_iterations:
        restart_count += 1
        remaining_budget = max_iterations - total_explored
        
        if remaining_budget < 100:
            break
            
        # Chọn một trạng thái ngẫu nhiên từ explored để restart
        if len(explored_global) > 10:
            # Lấy mẫu một số trạng thái đã explore
            sample_size = min(20, len(explored_global))
            candidate_boards = random.sample(list(explored_global), sample_size)
            
            # Chọn trạng thái có heuristic hứa hẹn
            candidates_with_h = [(b, heuristic(b)) for b in candidate_boards]
            candidates_with_h.sort(key=lambda x: x[1])
            
            # Chọn trong top 50% nhưng có tính ngẫu nhiên
            top_half = candidates_with_h[:len(candidates_with_h)//2 + 1]
            restart_board, restart_h = random.choice(top_half)
            
            if verbose:
                print(f"   Restart {restart_count}: Từ trạng thái h={restart_h}")
            
            # Explore từ trạng thái mới
            restart_node = Node(parent=None, board=restart_board, depth=0, 
                               g_value=0, h_value=restart_h)
            result_node, explored = explore_from_state(restart_board, restart_node, 
                                                       explored_global, remaining_budget)
            total_explored += explored
            
            if result_node.board.is_final_configuration():
                if verbose:
                    print(f"✅ Tìm thấy lời giải sau restart {restart_count}!")
                return Result(result_node, total_explored, result_node.g_value)
            
            # Cập nhật best node
            if result_node.h_value < best_h_overall:
                best_node_overall = result_node
                best_h_overall = result_node.h_value
                if verbose:
                    print(f"   → Cải thiện: h={best_h_overall}")

    # Nếu vẫn không tìm được, thử best-first search từ trạng thái tốt nhất
    if best_node_overall and best_h_overall < float('inf'):
        if verbose:
            print(f"   Thử best-first từ trạng thái tốt nhất (h={best_h_overall})...")
        
        remaining = max_iterations - total_explored
        if remaining > 100:
            # Tạo priority queue đơn giản
            from collections import deque
            queue = deque([(best_h_overall, best_node_overall)])
            visited_bf = set([best_node_overall.board])
            
            for _ in range(min(remaining, 1000)):
                if not queue:
                    break
                    
                _, current = queue.popleft()
                total_explored += 1
                
                if current.board.is_final_configuration():
                    if verbose:
                        print(f"✅ Best-first tìm được lời giải!")
                    return Result(current, total_explored, current.g_value)
                
                try:
                    moves = list(current.board.get_moves())
                    for move, cost in moves:
                        new_board = current.board.move_vehicle(move)
                        if new_board in visited_bf:
                            continue
                        visited_bf.add(new_board)
                        h_val = heuristic(new_board)
                        new_node = Node(current, new_board, current.depth + 1,
                                       current.g_value + cost, h_val)
                        # Insert theo thứ tự heuristic
                        inserted = False
                        for i, (h, _) in enumerate(queue):
                            if h_val < h:
                                queue.insert(i, (h_val, new_node))
                                inserted = True
                                break
                        if not inserted:
                            queue.append((h_val, new_node))
                except Exception:
                    continue

    if verbose:
        print(f"❌ Không tìm thấy lời giải sau {total_explored} trạng thái")
        print(f"   Best h đạt được: {best_h_overall}")
    
    raise NoSolutionFoundException(
        f"Hill Climbing không tìm được lời giải. "
        f"Explored {total_explored} states, best h={best_h_overall}"
    )