# app/result_overlay.py
import pygame
import config as cfg


class ResultOverlay:
    """
    Overlay đè lên màn hình game để hiển thị kết quả sau khi giải xong.

    Cách dùng:
        res = ResultOverlay()
        res.open(screen, {
            'algorithm': 'A*',
            'level': 3,
            'explored': 1234,
            'steps': 27,
            'search_time': 0.1234,   # giây
            'memory_mb': 12.34,
            'cost': 27
        })

    metrics: dict gồm các key ở trên. Thiếu key sẽ được điền giá trị mặc định.
    """

    def __init__(self, panel_w: int = 520, panel_h: int = 400):
        # Trạng thái overlay
        self.visible = False
        self.screen = None
        self.metrics = {}

        # Kích thước / vị trí panel
        self.panel_w = panel_w
        self.panel_h = panel_h
        self.panel_rect = pygame.Rect(
            (cfg.WINDOW_WIDTH  - panel_w) // 2,
            (cfg.WINDOW_HEIGHT - panel_h) // 2,
            panel_w, panel_h
        )

        # Font (đơn giản, dễ đọc)
        self.font_title = pygame.font.SysFont("arial", 24, bold=True)
        self.font_label = pygame.font.SysFont("arial", 18, bold=True)
        self.font_value = pygame.font.SysFont("consolas", 18)

        # Nút OK
        self.btn_w = 120
        self.btn_h = 36
        self.btn_ok = pygame.Rect(
            self.panel_rect.centerx - self.btn_w // 2,
            self.panel_rect.bottom - 20 - self.btn_h,
            self.btn_w, self.btn_h
        )

        # Nút đóng
        self.close_rect = pygame.Rect(self.panel_rect.right - 34, self.panel_rect.top + 10, 24, 24)

        # Màu sắc cơ bản
        self.col_dim     = (0, 0, 0, 150)      # nền mờ
        self.col_panel   = cfg.COLOR_BRIGHT_WHITE
        self.col_border  = cfg.COLOR_BRIGHT_BLACK
        self.col_text    = cfg.COLOR_BLACK
        self.col_muted   = cfg.COLOR_GRAY
        self.col_primary = cfg.COLOR_BRIGHT_BLUE
        self.col_white   = cfg.COLOR_BRIGHT_WHITE

    # ------------------------------
    # API
    # ------------------------------
    def open(self, screen, metrics: dict):
        """Mở overlay với dữ liệu kết quả."""
        self.screen = screen
        self.metrics = metrics or {}
        self.visible = True

    def close(self):
        """Đóng overlay."""
        self.visible = False
        self.metrics = {}

    # ------------------------------
    # Vẽ thành phần đơn giản
    # ------------------------------
    def _draw_button(self, rect: pygame.Rect, text: str):
        pygame.draw.rect(self.screen, self.col_primary, rect, border_radius=8)
        pygame.draw.rect(self.screen, self.col_border, rect, 2, border_radius=8)
        t = self.font_label.render(text, True, self.col_white)
        self.screen.blit(t, t.get_rect(center=rect.center))

    def _draw_kv_row(self, y: int, label: str, value: str, label_w: int = 160, xpad: int = 24):
        """Vẽ một dòng 'nhãn : giá trị'."""
        lx = self.panel_rect.x + xpad
        vx = self.panel_rect.x + xpad + label_w

        lsurf = self.font_label.render(label, True, self.col_muted)
        vsurf = self.font_value.render(value, True, self.col_text)

        self.screen.blit(lsurf, (lx, y))
        self.screen.blit(vsurf, (vx, y))

    # ------------------------------
    # Vẽ overlay
    # ------------------------------
    def draw(self):
        if not self.visible or self.screen is None:
            return

        # 1) Nền mờ
        dim = pygame.Surface((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT), pygame.SRCALPHA)
        dim.fill(self.col_dim)
        self.screen.blit(dim, (0, 0))

        # 2) Panel
        pygame.draw.rect(self.screen, self.col_panel, self.panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.col_border, self.panel_rect, 2, border_radius=12)

        # 3) Tiêu đề
        title = self.font_title.render("Result Summary", True, self.col_text)
        self.screen.blit(title, (self.panel_rect.x + 24, self.panel_rect.y + 16))

        # 4) Nút đóng
        pygame.draw.rect(self.screen, (235, 235, 235), self.close_rect, border_radius=6)
        pygame.draw.rect(self.screen, self.col_border, self.close_rect, 1, border_radius=6)
        xsurf = self.font_label.render("-", True, self.col_text)
        self.screen.blit(xsurf, xsurf.get_rect(center=self.close_rect.center))

        # 5) Dữ liệu kết quả (định dạng tối giản)
        #    Lấy giá trị có sẵn hoặc mặc định
        algo   = str(self.metrics.get('algorithm', '?'))
        level  = str(self.metrics.get('level', '?'))
        expl   = f"{int(self.metrics.get('explored', 0)):,}"
        steps  = f"{int(self.metrics.get('steps', 0)):,}"
        t_sec  = f"{float(self.metrics.get('search_time', 0.0)):.4f} s"
        mem    = f"{float(self.metrics.get('memory_mb', 0.0)):.2f} MB"
        cost   = str(self.metrics.get('cost', 0))

        y0 = self.panel_rect.y + 70
        gap = 32
        self._draw_kv_row(y0 + 0*gap, "Algorithm:",   algo)
        self._draw_kv_row(y0 + 1*gap, "Level:",       level)
        self._draw_kv_row(y0 + 2*gap, "Nodes explored:", expl)
        self._draw_kv_row(y0 + 3*gap, "Steps:",       steps)
        self._draw_kv_row(y0 + 4*gap, "Search time:", t_sec)
        self._draw_kv_row(y0 + 5*gap, "Memory used:", mem)
        self._draw_kv_row(y0 + 6*gap, "Total cost:",  cost)

        # 6) Nút OK
        self._draw_button(self.btn_ok, "OK")

    # ------------------------------
    # Xử lý sự kiện
    # ------------------------------
    def handle_event(self, event):
        """Trả về 'close' nếu người dùng đóng overlay, ngược lại trả về None."""
        if not self.visible:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                return 'close'

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.close_rect.collidepoint(mx, my):
                return 'close'
            if self.btn_ok.collidepoint(mx, my):
                return 'close'

        return None
