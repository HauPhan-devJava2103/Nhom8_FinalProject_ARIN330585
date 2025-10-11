import time
import pygame
import config as cfg
from memory_profiler import memory_usage
from model.node import get_history
from algorithm import (
    a_star, breadth_first_search, depth_first_search,
    uniform_cost_search, greedy_search, beam_search,
    backtracking, ac3_search,
    belief_blind_search, And_Or_Search, hill_climbing_search
)
from .assets import load_vehicle_images, select_board, init_audio
from .ui import show_image, show_text, show_board
from . import control as ctl
from .selection_overlay import SelectionOverlay
from .result_overlay import ResultOverlay

#  Stats Manager - Tạo thống kê
class StatsManager:
    def __init__(self):
        self.rows = []  # list[dict]
        try:
            import plotly.io as pio
            if not pio.renderers.default:
                pio.renderers.default = "browser"
        except Exception:
            pass

    def add(self, stats: dict):
        self.rows.append(stats)

    @staticmethod
    def _to_int_or_none(v):
        try:
            return int(v)
        except Exception:
            return None

    def draw_runtime_chart(self, level: int):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import os, webbrowser, tempfile
        import plotly.io as pio

        target_level = self._to_int_or_none(level)
        data = [r for r in self.rows if self._to_int_or_none(r.get("level")) == target_level]
        if not data:
            print(f"[Chart] Không có dữ liệu thống kê cho level {level}")
            return

        algorithms = sorted({r["algorithm"] for r in data})
        metrics = {"Thời gian chạy (s)": [], "Bộ nhớ (MB)": [], "Số trạng thái mở rộng": [], "Chi phí lời giải": []}

        for algo in algorithms:
            subset = [r for r in data if r["algorithm"] == algo]
            metrics["Thời gian chạy (s)"].append(sum(r["search_time"] for r in subset) / len(subset))
            metrics["Bộ nhớ (MB)"].append(sum(r["memory_mb"] for r in subset) / len(subset))
            metrics["Số trạng thái mở rộng"].append(sum(r["explored"] for r in subset) / len(subset))
            metrics["Chi phí lời giải"].append(sum(r["cost"] for r in subset) / len(subset))

        fig = make_subplots(rows=2, cols=2, subplot_titles=list(metrics.keys()),
                            vertical_spacing=0.15, horizontal_spacing=0.1)

        colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA']
        symbols = ['circle', 'square', 'diamond', 'cross']

        for i, (name, values) in enumerate(metrics.items()):
            row, col = divmod(i, 2); row += 1; col += 1
            text_values = []
            for v in values:
                if isinstance(v, float):
                    text_values.append(f"{v:.3f}".rstrip("0").rstrip("."))
                else:
                    text_values.append(f"{v:,}")
            fig.add_trace(
                go.Scatter(
                    x=algorithms, y=values,
                    mode="lines+markers+text", name=name,
                    text=text_values, textposition="top center",
                    marker=dict(size=12, color=colors[i], symbol=symbols[i],
                                line=dict(width=2, color='DarkSlateGrey')),
                    line=dict(width=3, color=colors[i]),
                    hoverinfo='x+y+name',
                ),
                row=row, col=col
            )

        fig.update_layout(
            title_text=f"<b>SO SÁNH HIỆU SUẤT THUẬT TOÁN — LEVEL {level}</b>",
            title_font=dict(size=22, color='black'),
            showlegend=False, height=850, width=1000,
            template='plotly_white', margin=dict(l=40, r=40, t=80, b=50),
            plot_bgcolor='rgba(250,250,250,0.9)', hovermode='x unified'
        )
        fig.update_xaxes(tickangle=-20, linecolor='gray', mirror=True)
        fig.update_yaxes(showline=True, linecolor='gray', mirror=True)

        try:
            tmpdir = tempfile.gettempdir()
            out_path = os.path.join(tmpdir, f"stats_level_{level}.html")
            pio.write_html(fig, file=out_path, auto_open=False, include_plotlyjs="cdn", full_html=True)
            webbrowser.open(f"file://{out_path}")
            print(f"[Chart] Đã mở biểu đồ trong trình duyệt: {out_path}")
        except Exception as e:
            print(f"[Chart] Không mở được trình duyệt ({e}). Fallback sang fig.show().")
            try:
                fig.show(config={'displayModeBar': True})
            except Exception as e2:
                print(f"[Chart] fig.show() cũng lỗi: {e2}. Bạn có thể mở file HTML thủ công.")


#  Utilities - Ánh xạ các thuật toán

def _algorithm_of(name: str):
    mapping = {"BFS": breadth_first_search, "DFS": depth_first_search,
               "UCS": uniform_cost_search, "A*": a_star,
               "Greedy": greedy_search, "Beam": beam_search,
               "Partially_Observation": belief_blind_search,
               "BackTrack": backtracking, "AC3": ac3_search,
               "Hill_Climbing": hill_climbing_search, "And_Or_Search": And_Or_Search}
    if name not in mapping:
        raise ValueError(f"Unknown algorithm: {name}")
    return mapping[name]

#  Game Entry

# Khởi động game
def run():
    pygame.init(); pygame.font.init()
    screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
    pygame.display.set_caption("Rush Hour — Manual & Solver")
    clock = pygame.time.Clock()

    click_sound, error_sound = init_audio()
    images = load_vehicle_images()
    sound_on = True

    from .screens import start_screen
    running = True
    stats_mgr = StatsManager()  # GIỮ để lưu thuật toán

    # Vòng lặp logic trong game
    while running:
        signal, sound_on = start_screen(screen, click_sound, sound_on)
        if signal == "quit":
            break

        levels = list(range(1, 13))
        algos = ["BFS", "DFS", "UCS", "A*", "Greedy", "Beam",
                 "Partially_Observation", "BackTrack", "AC3",
                 "Hill_Climbing", "And_Or_Search"]

        level_selected = 1
        algorithm_selected = "BFS"

        sel_overlay = SelectionOverlay(levels, algos, init_level=level_selected, init_algo=algorithm_selected)
        res_overlay = ResultOverlay()

        # load + solve lần đầu
        board0 = select_board(level_selected)
        history_boards, stats = _solve_capture(
            board0, algorithm_selected, level_selected,
            screen, click_sound, error_sound, sound_on
        )
        stats_mgr.add(stats)  # LƯU THỐNG KÊ CHO THUẬT TOÁN

        nav = play_loop(screen, images, click_sound, sound_on,
                        level_selected, algorithm_selected,
                        board0, history_boards, stats, stats_mgr,
                        sel_overlay, res_overlay, clock)
        if nav == "quit":
            running = False

    pygame.quit()

def _solve_capture(board0, algorithm_selected, level_selected, screen, click_sound, error_sound, sound_on):
    """Chạy solver & trả (history_boards, stats)."""
    try:
        t0 = time.perf_counter()
        mem_usage_mb, res = memory_usage((_algorithm_of(algorithm_selected), (board0,)),
                                         retval=True, max_usage=True)
        t1 = time.perf_counter()
        history_boards = get_history(res.node)
        steps = max(0, len(history_boards) - 1)

        stats = {
            "algorithm": algorithm_selected,
            "level": int(level_selected),
            "explored": getattr(res, "number_of_explored_states", 0),
            "steps": steps,
            "search_time": float(t1 - t0),
            "memory_mb": float(mem_usage_mb),
            "cost": getattr(res, "cost", 0),
        }
        print(f"[Stats] {algorithm_selected} | Lv{stats['level']} | "
              f"Explored={stats['explored']} | Steps={stats['steps']} | Cost={stats['cost']} | "
              f"Time={stats['search_time']:.3f}s | Mem={stats['memory_mb']:.2f}MB")
        return history_boards, stats
    except Exception:
        if sound_on and error_sound:
            try: error_sound.play()
            except Exception: pass
        pygame.draw.rect(screen, cfg.COLOR_YELLOW,
                         (cfg.WINDOW_WIDTH // 2 - 200, cfg.WINDOW_HEIGHT // 2 - 50, 400, 100), border_radius=20)
        show_text(screen, "No solution is found", 40, cfg.COLOR_RED,
                  (cfg.WINDOW_WIDTH // 2, cfg.WINDOW_HEIGHT // 2))
        pygame.display.update(); pygame.time.wait(1500)
        stats = {"algorithm": algorithm_selected, "level": int(level_selected),
                 "explored": 0, "steps": 0, "search_time": 0.0, "memory_mb": 0.0, "cost": 0}
        return [[board0, 0]], stats

# Vòng lặp chính trò chơi
def play_loop(screen, images, click_sound, sound_on,
              level_selected, algorithm_selected,
              board0, history_boards, stats, stats_mgr: StatsManager,
              sel_overlay: SelectionOverlay, res_overlay: ResultOverlay, clock: pygame.time.Clock):
    # 2 chế độ Manual và chế độ Auto-Algorithms
    manual_mode = True
    selected_vid = None
    auto_play = False
    pause = True

    current_step = 0
    board = board0
    end_game_logged = False
    overlay_select_open = False
    overlay_result_open = False

    # Manual stats
    manual_steps = 0
    manual_cost = 0
    manual_start_t = time.perf_counter()

    # Dừng thời gian khi finish
    manual_finished = False
    manual_elapsed = 0.0

    while True:
        show_image(screen, 'background.png')

        # Header
        if manual_mode:
            elapsed = manual_elapsed if manual_finished else (time.perf_counter() - manual_start_t)
            show_text(screen, "MANUAL MODE", 18, cfg.COLOR_BRIGHT_GREEN, (cfg.WINDOW_WIDTH // 2, 40))
            show_text(screen, f"Moves: {manual_steps}  |  Cost: {manual_cost}  |  Time: {elapsed:.2f}s",
                      16, cfg.COLOR_WHITE, (cfg.WINDOW_WIDTH // 2, 70))
            show_text(screen, "Click a car, then use W/A/S/D or Arrow Keys to move",
                      16, cfg.COLOR_WHITE, (cfg.WINDOW_WIDTH // 2, 95))
        else:
            show_text(screen, f"AUTO: Step {current_step + 1}/{len(history_boards)}",
                      20, cfg.COLOR_WHITE, (cfg.WINDOW_WIDTH // 2, 40))
            show_text(screen, f"Total cost: {history_boards[min(current_step, len(history_boards)-1)][1]}",
                      18, cfg.COLOR_WHITE, (cfg.WINDOW_WIDTH // 2, 70))

        show_text(screen, "M: manual/auto | SPACE: pause/resume | R: restart | ESC: Quit",
                  16, cfg.COLOR_BRIGHT_WHITE, (cfg.WINDOW_WIDTH // 2, cfg.WINDOW_HEIGHT - 20))

        pygame.draw.rect(screen, cfg.COLOR_BLACK,
                         (cfg.BOARD_X, cfg.BOARD_Y, cfg.BOARD_WIDTH, cfg.BOARD_HEIGHT), width=1)

        mouse_pos = pygame.mouse.get_pos()
        for (x, y), name in zip(cfg.button_xy, cfg.button_names):
            from .ui import show_image as _show_img
            _show_img(screen, name, (cfg.BUTTON_TOOL, cfg.BUTTON_TOOL), (x, y))
            if name == "pause.png" and (not manual_mode) and pause:
                _show_img(screen, "resume.png", (cfg.BUTTON_TOOL, cfg.BUTTON_TOOL), (x, y))
            if name == "sound.png" and not sound_on:
                _show_img(screen, 'noSound.png', (cfg.BUTTON_TOOL, cfg.BUTTON_TOOL), (x, y))

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            # Overlay trước
            if overlay_result_open and res_overlay.visible:
                act = res_overlay.handle_event(event)
                if act == 'close':
                    res_overlay.close(); overlay_result_open = False
                continue

            if overlay_select_open and sel_overlay.visible:
                result = sel_overlay.handle_event(event)
                if result:
                    action, lv, algo = result
                    if action == 'apply':
                        level_selected, algorithm_selected = int(lv), algo
                        board0 = select_board(level_selected)
                        history_boards, stats = _solve_capture(
                            board0, algorithm_selected, level_selected,
                            screen, click_sound, None, sound_on
                        )
                        stats_mgr.add(stats)  # LƯU THUẬT TOÁN
                        # Reset trạng thái
                        current_step = 0
                        board = board0
                        manual_mode = True
                        auto_play = False
                        pause = True
                        end_game_logged = False
                        overlay_result_open = False

                        # Reset manual
                        manual_steps = 0
                        manual_cost = 0
                        manual_start_t = time.perf_counter()
                        manual_finished = False
                        manual_elapsed = 0.0

                        sel_overlay.close(); overlay_select_open = False
                    elif action == 'cancel':
                        sel_overlay.close(); overlay_select_open = False
                continue

            # Gameplay
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"

                elif event.key == pygame.K_m:
                    # Chuyển chế độ
                    manual_mode = not manual_mode
                    if manual_mode:
                        auto_play = False
                        pause = True
                        # Reset manual khi quay lại manual
                        manual_steps = 0
                        manual_cost = 0
                        manual_start_t = time.perf_counter()
                        manual_finished = False
                        manual_elapsed = 0.0
                    else:
                        pause = False
                        auto_play = True

                elif (not manual_mode) and event.key == pygame.K_SPACE:
                    pause = not pause
                    auto_play = not pause

                elif event.key == pygame.K_r:
                    # Restart
                    current_step = 0
                    board = board0
                    auto_play = False
                    pause = True
                    end_game_logged = False
                    overlay_result_open = False
                    # Reset manual
                    manual_steps = 0
                    manual_cost = 0
                    manual_start_t = time.perf_counter()
                    manual_finished = False
                    manual_elapsed = 0.0

                elif manual_mode and (not manual_finished) and selected_vid is not None and event.key in ctl.DIR_KEYS:
                    # Di chuyển trong manual (khóa khi đã finish)
                    dir_char = ctl.DIR_KEYS[event.key]
                    new_board, moved, move_cost = ctl.try_apply_move(board, selected_vid, dir_char)
                    if moved:
                        board = new_board
                        manual_steps += 1
                        manual_cost  += move_cost
                        try:
                            click_sound.play() if sound_on else None
                        except Exception:
                            pass

                        # Thắng -> đóng băng thời gian, khóa điều khiển & mở overlay (KHÔNG lưu stats_mgr)
                        if board.is_final_configuration():
                            manual_elapsed = time.perf_counter() - manual_start_t
                            manual_finished = True
                            manual_result = {
                                "algorithm": "Manual",
                                "level": int(level_selected),
                                "explored": 0,
                                "steps": manual_steps,
                                "search_time": float(manual_elapsed),
                                "memory_mb": 0.0,
                                "cost": manual_cost,
                            }
                            res_overlay.open(screen, manual_result)
                            overlay_result_open = True
                            # Dừng auto/pause cho chắc
                            auto_play = False
                            pause = True

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Click chọn xe (chỉ dùng cho manual; vẫn cho phép chọn sau khi win nhưng không di chuyển được do manual_finished=True)
                vid = ctl.vid_at_mouse(board, mouse_pos := pygame.mouse.get_pos())
                selected_vid = vid if vid != -1 else None

                # Click vào các nút
                for (x, y), name in zip(cfg.button_xy, cfg.button_names):
                    rect = pygame.Rect(x, y, cfg.BUTTON_TOOL, cfg.BUTTON_TOOL)
                    if not rect.collidepoint(mouse_pos):
                        continue

                    if name == "home.png":
                        return "home"

                    elif name == "level.png":
                        sel_overlay.open(screen); overlay_select_open = True

                    elif name == "analytics.png":
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            stats_mgr.draw_runtime_chart(level_selected)  # chỉ dữ liệu solver
                        else:
                            # Mở overlay kết quả của LẦN GIẢI BẰNG THUẬT TOÁN gần nhất (biến stats)
                            res_overlay.open(screen, stats); overlay_result_open = True

                    elif name == "sound.png":
                        sound_on = not sound_on
                        try:
                            pygame.mixer.music.unpause() if sound_on else pygame.mixer.music.pause()
                        except Exception:
                            pass

                    elif name == "pause.png":
                        if not manual_mode:
                            pause = not pause
                            auto_play = not pause
                            try:
                                click_sound.play() if sound_on else None
                            except Exception:
                                pass

                    elif name == "restart.png":
                        current_step = 0
                        board = board0
                        auto_play = False
                        pause = True
                        end_game_logged = False
                        overlay_result_open = False
                        # Reset manual
                        manual_steps = 0
                        manual_cost = 0
                        manual_start_t = time.perf_counter()
                        manual_finished = False
                        manual_elapsed = 0.0
                        try:
                            click_sound.play() if sound_on else None
                        except Exception:
                            pass

        # Render board
        if manual_mode:
            show_board(screen, board, images, selected_vid=selected_vid)
        else:
            if auto_play:
                pygame.time.wait(150)
                current_step = min(current_step + 1, len(history_boards) - 1)
            show_board(screen, history_boards[current_step][0], images)

            if current_step >= len(history_boards) - 1 and not end_game_logged:
                res_overlay.open(screen, stats)
                overlay_result_open = True
                end_game_logged = True
                auto_play = False
                pause = True

        # Vẽ overlay (nếu có)
        if overlay_select_open: sel_overlay.draw()
        if overlay_result_open: res_overlay.draw()

        pygame.display.update()
        clock.tick(60)
