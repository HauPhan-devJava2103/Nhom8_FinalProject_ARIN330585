# algorithm/belief_blind_search.py
from collections import deque
from dataclasses import replace
from typing import FrozenSet, Iterable, List, Set, Tuple

from model.board import Board
from model.node import Node
from model.move import Move
from algorithm.result import Result
from algorithm.exception import NoSolutionFoundException


# ===== Helpers =====

def _canonical_belief(belief: Iterable[Board]) -> FrozenSet[Board]:
    """Đưa belief về dạng frozenset để hash/so sánh được."""
    return frozenset(belief)

def _is_goal_belief(belief: FrozenSet[Board]) -> bool:
    """Đích khi TẤT CẢ các trạng thái trong belief đều tới đích."""
    return all(b.is_final_configuration() for b in belief)

def _vehicle_index_by_id(board: Board, vid: int) -> int:
    for idx, v in enumerate(board.vehicles):
        if v.id == vid:
            return idx
    return -1

def _moves_of_board_as_specs(board: Board) -> Set[Tuple[int, int]]:
    """
    Trả về tập các 'spec' nước đi của board dưới dạng (vehicle_id, dir),
    với dir ∈ {-1, +1}. Bỏ qua cost & index để có thể giao cắt trên nhiều board.
    """
    specs: Set[Tuple[int, int]] = set()
    for mv, _ in board.get_moves():
        # Lưu dưới dạng (id xe, hướng) để có thể intersect giữa các board
        specs.add((mv.vehicle_id, 1 if mv.move > 0 else -1))
    return specs

def _common_safe_moves(belief: FrozenSet[Board]) -> Set[Tuple[int, int]]:
    """
    Intersection các nước đi (vehicle_id, dir) hợp lệ trên MỌI board
    trong belief. Chỉ những nước này mới an toàn cho kế hoạch conformant.
    """
    itr = iter(belief)
    try:
        first = next(itr)
    except StopIteration:
        return set()

    common = _moves_of_board_as_specs(first)
    for b in itr:
        common &= _moves_of_board_as_specs(b)
        if not common:
            break
    return common

def _apply_spec_to_board(board: Board, spec: Tuple[int, int]) -> Board | None:
    """
    Áp dụng 1 spec (vehicle_id, dir) lên 1 board.
    Nếu không thực hiện được (do khác biệt vị trí/va chạm), trả None.
    Lưu ý: spec này được đảm bảo hợp lệ với board nếu spec đến từ _common_safe_moves,
    tuy nhiên ta vẫn kiểm tra phòng hờ.
    """
    vid, dir_ = spec
    idx = _vehicle_index_by_id(board, vid)
    if idx < 0:
        return None
    move = Move(vehicle_id=vid, vehicle_index=idx, move=dir_)
    # Xác nhận hợp lệ bằng cách đối chiếu forward/backward ở get_moves
    legal = False
    for mv, _ in board.get_moves():
        if mv.vehicle_id == vid and (1 if mv.move > 0 else -1) == dir_:
            legal = True
            break
    if not legal:
        return None
    return board.move_vehicle(move)

def _successor_belief(belief: FrozenSet[Board], spec: Tuple[int, int]) -> FrozenSet[Board] | None:
    """
    Chuyển belief bằng cách áp 1 nước đi spec lên TỪNG board.
    Nếu với board nào đó spec không áp dụng được -> spec không còn 'an toàn' (bỏ).
    """
    next_states: List[Board] = []
    for b in belief:
        nb = _apply_spec_to_board(b, spec)
        if nb is None:
            return None  # không an toàn trên một số state -> loại
        next_states.append(nb)
    return _canonical_belief(next_states)


# ===== Blind Belief Search (BFS trên belief space) =====

def belief_blind_search(board: Board, max_nodes: int = 1_000_000) -> Result:
    """
    Blind Belief Search (BFS) trên không gian belief:
    - Nút là Node với board=None và belief=FrozenSet[Board].
    - Chỉ áp dụng các nước đi an toàn cho mọi state trong belief (intersection).
    - Đích khi tất cả state trong belief đều đích.
    - Chi phí hành động đặt = 1 mỗi bước (mù/không heuristic).
    """
    # Belief khởi đầu là trạng thái biết chắc (một board)
    root_belief = _canonical_belief([board])
    root = Node(parent=None, board=None, belief=root_belief, depth=0, g_value=0, h_value=0)

    if _is_goal_belief(root_belief):
        return Result(root, number_of_explored_states=1, cost=0)

    frontier: deque[Node] = deque([root])
    visited: Set[FrozenSet[Board]] = {root_belief}
    explored = 0

    while frontier:
        node = frontier.popleft()
        explored += 1
        if explored >= max_nodes:
            break

        belief = node.belief
        if belief is None:
            # safety: nếu vì lý do nào đó node chỉ có board (không mong đợi)
            belief = _canonical_belief([node.board]) if node.board is not None else _canonical_belief([])

        # Lấy intersection các moves an toàn
        safe_specs = _common_safe_moves(belief)
        if not safe_specs:
            continue  # không có nước đi áp dụng cho tất cả — bế tắc

        for spec in safe_specs:
            nb = _successor_belief(belief, spec)
            if nb is None:
                continue  # phòng hờ, dù theo lý thuyết không xảy ra

            if nb in visited:
                continue
            visited.add(nb)

            # g_value +1 cho mỗi bước (blind)
            child = Node(
                parent=node,
                board=None,
                belief=nb,
                depth=node.depth + 1,
                g_value=node.g_value + 1,
                h_value=0,
            )

            if _is_goal_belief(nb):
                # Tổng cost = g_value (mỗi bước = 1),
                return Result(child, number_of_explored_states=len(visited), cost=child.g_value)

            frontier.append(child)

    # Không tìm được nghiệm
    raise NoSolutionFoundException()
