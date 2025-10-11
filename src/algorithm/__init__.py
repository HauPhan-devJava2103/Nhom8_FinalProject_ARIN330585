"""
Gói thuật toán cho trò chơi Rush Hour.
Tự động import các thuật toán có sẵn.
"""

from importlib import import_module

# Danh sách các module cần import
_modules = [
    "bfs",
    "dfs",
    "ucs",
    "greedySearch",
    "beamSearch",
    "backtrackingSearch",
    "belief_blind_search",
    "ac3Search",
    "astar",
    "hill_climbing",
    "and_or_search"
]

# Import an toàn từng module
for _m in _modules:
    try:
        import_module(f".{_m}", package=__name__)
    except ModuleNotFoundError:
        print(f"⚠️ Cảnh báo: không tìm thấy module '{_m}.py' trong thư mục algorithm.")

# Import cụ thể từng hàm có sẵn
try:
    from .bfs import breadth_first_search
    from .dfs import depth_first_search
    from .ucs import uniform_cost_search
    from .greedySearch import greedy_search
    from .beamSearch import beam_search
    from .backtrackingSearch import backtracking
    from .belief_blind_search import belief_blind_search
    from .ac3Search import ac3_search
    from .astar import a_star
    from .hill_climbing import hill_climbing_search
    from .and_or_search import And_Or_Search
except ModuleNotFoundError:
    pass

from .exception import NoSolutionFoundException
from .result import Result

__all__ = [
    "breadth_first_search",
    "depth_first_search",

    "uniform_cost_search",
    "greedy_search",
    "a_star",

    "beam_search",
    "hill_climbing_search",

    "backtracking",
    "ac3_search",

    "belief_blind_search",
    "And_Or_Search",
    
    "NoSolutionFoundException",
    "Result",
]
