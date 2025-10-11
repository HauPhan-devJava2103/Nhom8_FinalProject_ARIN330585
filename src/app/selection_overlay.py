# app/selection_overlay.py
import pygame
import config as cfg

class SelectionOverlay:
    """
    Overlay chọn Level (lưới) và Algorithm (danh sách đơn) có hỗ trợ SCROLL.
    Trả về từ handle_event:
        ('apply', level, algo) | ('cancel', None, None) | None
    """

    def __init__(self, levels, algos, init_level=1, init_algo="BFS",
                 panel_w=620, panel_h=400):
        # dữ liệu
        self.levels = [int(x) for x in levels]
        self.algos  = list(algos)
        self.selected_level = init_level if init_level in self.levels else (self.levels[0] if self.levels else 1)
        self.selected_algo  = init_algo  if init_algo  in self.algos  else (self.algos[0]  if self.algos  else "")

        # trạng thái
        self.visible = False
        self.screen  = None

        # panel
        self.panel_w = panel_w
        self.panel_h = panel_h
        self.panel_rect = pygame.Rect(
            (cfg.WINDOW_WIDTH  - panel_w) // 2,
            (cfg.WINDOW_HEIGHT - panel_h) // 2,
            panel_w, panel_h
        )

        # font
        self.font_title = pygame.font.SysFont("arial", 22, bold=True)
        self.font = pygame.font.SysFont("arial", 18, bold=True)

        # vùng trái/phải
        self.left_rect  = pygame.Rect(self.panel_rect.x + 20, self.panel_rect.y + 70,
                                      int(self.panel_w * 0.58), self.panel_h - 70 - 70)
        self.right_rect = pygame.Rect(self.left_rect.right + 10, self.left_rect.y,
                                      self.panel_rect.right - 20 - (self.left_rect.right + 10),
                                      self.left_rect.h)

        # lưới level (cố định, đơn giản)
        self.level_cols = 5
        self.level_cell_w = 56
        self.level_cell_h = 36
        self.level_gap = 8

        # nút
        self.btn_w, self.btn_h = 120, 36
        self.btn_apply = pygame.Rect(self.panel_rect.right - 20 - self.btn_w,
                                     self.panel_rect.bottom - 20 - self.btn_h,
                                     self.btn_w, self.btn_h)
        self.btn_cancel = pygame.Rect(self.btn_apply.left - 10 - self.btn_w,
                                      self.btn_apply.top,
                                      self.btn_w, self.btn_h)

        # màu
        self.dim_alpha = 150
        self.c_panel   = cfg.COLOR_BRIGHT_WHITE
        self.c_border  = cfg.COLOR_BRIGHT_BLACK
        self.c_text    = cfg.COLOR_BLACK
        self.c_muted   = cfg.COLOR_GRAY
        self.c_fill    = (230, 230, 230)
        self.c_sel     = (255, 230, 120)
        self.c_primary = cfg.COLOR_BRIGHT_BLUE
        self.c_white   = cfg.COLOR_BRIGHT_WHITE

        # nút đóng
        self.close_rect = pygame.Rect(self.panel_rect.right - 34, self.panel_rect.top + 10, 24, 24)

        # --------- SCROLL CHO ALGORITHM ----------
        self.item_h = 36                 # chiều cao 1 item
        self.scroll_y = 0                # offset cuộn hiện tại
        self.scroll_step = self.item_h   # mỗi nấc cuộn = 1 item
        self.scrollbar_w = 10            # bề rộng thanh cuộn
        self._dragging_bar = False
        self._drag_offset = 0            # offset chuột trong thumb khi bắt đầu kéo
        # -----------------------------------------

    # ---------------- API ----------------
    def open(self, screen):
        self.screen = screen
        self.visible = True

    def close(self):
        self.visible = False

    # -------------- DRAW -----------------
    def draw(self):
        if not self.visible:
            return

        # nền mờ
        dim = pygame.Surface((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, self.dim_alpha))
        self.screen.blit(dim, (0, 0))

        # panel
        pygame.draw.rect(self.screen, self.c_panel, self.panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.c_border, self.panel_rect, 2, border_radius=12)

        # title
        title = self.font_title.render("Select Level & Algorithm", True, self.c_text)
        self.screen.blit(title, (self.panel_rect.x + 20, self.panel_rect.y + 16))

        # nút đóng
        pygame.draw.rect(self.screen, (235, 235, 235), self.close_rect, border_radius=6)
        pygame.draw.rect(self.screen, self.c_border, self.close_rect, 1, border_radius=6)
        xsurf = self.font.render("-", True, self.c_text)
        self.screen.blit(xsurf, xsurf.get_rect(center=self.close_rect.center))

        # khung trái: Level
        pygame.draw.rect(self.screen, self.c_white, self.left_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.c_border, self.left_rect, 1, border_radius=10)
        lblL = self.font.render("Level", True, self.c_muted)
        self.screen.blit(lblL, (self.left_rect.x, self.left_rect.y - 26))

        # vẽ các ô level
        x0 = self.left_rect.x + 10
        y0 = self.left_rect.y + 10
        for i, lv in enumerate(self.levels):
            col = i % self.level_cols
            row = i // self.level_cols
            x = x0 + col * (self.level_cell_w + self.level_gap)
            y = y0 + row * (self.level_cell_h + self.level_gap)
            r = pygame.Rect(x, y, self.level_cell_w, self.level_cell_h)
            color = self.c_sel if lv == self.selected_level else self.c_fill
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            pygame.draw.rect(self.screen, self.c_border, r, 1, border_radius=8)

            t = self.font.render(str(lv), True, self.c_text)
            self.screen.blit(t, t.get_rect(center=r.center))

        # khung phải: Algorithm (vẽ nền + viền + nhãn)
        pygame.draw.rect(self.screen, self.c_white, self.right_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.c_border, self.right_rect, 1, border_radius=10)
        lblR = self.font.render("Algorithm", True, self.c_muted)
        self.screen.blit(lblR, (self.right_rect.x, self.right_rect.y - 26))

        # ----- VÙNG NỘI DUNG CUỘN ----- (bên trong right_rect, chừa padding 10)
        inner_x = self.right_rect.x + 10
        inner_y = self.right_rect.y + 10
        inner_w = self.right_rect.w - 20
        inner_h = self.right_rect.h - 20

        # khu vực clip để không vẽ tràn ra ngoài
        content_rect = pygame.Rect(inner_x, inner_y, inner_w, inner_h)
        self.screen.set_clip(content_rect)

        # tổng chiều cao nội dung & max_scroll
        content_h = len(self.algos) * self.item_h
        max_scroll = max(0, content_h - inner_h)
        if self.scroll_y > max_scroll: self.scroll_y = max_scroll
        if self.scroll_y < 0: self.scroll_y = 0

        # vùng dành cho list (chừa chỗ scrollbar)
        list_w = inner_w - (self.scrollbar_w + 6 if content_h > inner_h else 0)

        # vẽ từng item với offset cuộn
        for i, algo in enumerate(self.algos):
            y_item = inner_y - self.scroll_y + i * self.item_h
            r = pygame.Rect(inner_x, y_item, list_w, self.item_h - 6)
            if r.bottom < inner_y or r.top > inner_y + inner_h:
                continue  # bỏ qua item nằm ngoài vùng nhìn thấy

            color = self.c_sel if algo == self.selected_algo else self.c_fill
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            pygame.draw.rect(self.screen, self.c_border, r, 1, border_radius=8)

            # rút gọn nếu tên quá dài
            txt = algo
            while self.font.size(txt)[0] > r.w - 14 and len(txt) > 3:
                txt = txt[:-2] + "…"
            t = self.font.render(txt, True, self.c_text)
            self.screen.blit(t, t.get_rect(center=r.center))

        # vẽ scrollbar nếu cần
        if content_h > inner_h:
            track_x = inner_x + list_w + 6
            track = pygame.Rect(track_x, inner_y, self.scrollbar_w, inner_h)
            pygame.draw.rect(self.screen, (242, 242, 242), track, border_radius=6)
            pygame.draw.rect(self.screen, self.c_border, track, 1, border_radius=6)

            # thumb
            thumb_h = max(20, int(inner_h * inner_h / content_h))
            if max_scroll == 0:
                thumb_y = inner_y
            else:
                thumb_y = inner_y + int((inner_h - thumb_h) * (self.scroll_y / max_scroll))
            self._thumb_rect = pygame.Rect(track_x, thumb_y, self.scrollbar_w, thumb_h)

            pygame.draw.rect(self.screen, (210, 210, 210), self._thumb_rect, border_radius=6)
            pygame.draw.rect(self.screen, self.c_border, self._thumb_rect, 1, border_radius=6)
        else:
            self._thumb_rect = None

        # bỏ clip
        self.screen.set_clip(None)

        # nút Cancel & Apply
        self._draw_button(self.btn_cancel, "Cancel", primary=False)
        self._draw_button(self.btn_apply,  "Apply",  primary=True)

    def _draw_button(self, rect, text, primary):
        bg = self.c_primary if primary else self.c_panel
        fg = self.c_white   if primary else self.c_text
        pygame.draw.rect(self.screen, bg, rect, border_radius=8)
        pygame.draw.rect(self.screen, self.c_border, rect, 2, border_radius=8)
        t = self.font.render(text, True, fg)
        self.screen.blit(t, t.get_rect(center=rect.center))

    # -------------- EVENTS ---------------
    def handle_event(self, event):
        """
        Return:
          - ('apply', level, algo) khi nhấn Apply hoặc Enter
          - ('cancel', None, None) khi nhấn ESC/X/Cancel
          - None nếu chưa có hành động
        """
        if not self.visible:
            return None

        # phím tắt
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return ('cancel', None, None)
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return ('apply', self.selected_level, self.selected_algo)
            # đổi level nhanh bằng mũi tên
            if event.key in (pygame.K_LEFT, pygame.K_a):
                i = self.levels.index(self.selected_level)
                self.selected_level = self.levels[max(0, i - 1)]
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                i = self.levels.index(self.selected_level)
                self.selected_level = self.levels[min(len(self.levels) - 1, i + 1)]

        # ---- SCROLL BẰNG BÁNH XE ----
        if event.type == pygame.MOUSEWHEEL:
            # pygame: event.y > 0 là lăn lên
            content_h = len(self.algos) * self.item_h
            inner_h = self.right_rect.h - 20
            max_scroll = max(0, content_h - inner_h)
            if max_scroll > 0:
                self.scroll_y -= event.y * self.scroll_step
                self.scroll_y = max(0, min(self.scroll_y, max_scroll))
            return None

        # chuột
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # đóng
            if self.close_rect.collidepoint(mx, my):
                return ('cancel', None, None)

            # nút
            if self.btn_cancel.collidepoint(mx, my):
                return ('cancel', None, None)
            if self.btn_apply.collidepoint(mx, my):
                return ('apply', self.selected_level, self.selected_algo)

            # click chọn level
            x0 = self.left_rect.x + 10
            y0 = self.left_rect.y + 10
            for i, lv in enumerate(self.levels):
                col = i % self.level_cols
                row = i // self.level_cols
                x = x0 + col * (self.level_cell_w + self.level_gap)
                y = y0 + row * (self.level_cell_h + self.level_gap)
                r = pygame.Rect(x, y, self.level_cell_w, self.level_cell_h)
                if r.collidepoint(mx, my):
                    self.selected_level = lv
                    break

            # click chọn algorithm (tính đến scroll)
            inner_x = self.right_rect.x + 10
            inner_y = self.right_rect.y + 10
            inner_w = self.right_rect.w - 20
            inner_h = self.right_rect.h - 20
            list_w = inner_w - (self.scrollbar_w + 6 if len(self.algos)*self.item_h > inner_h else 0)

            # chỉ xử lý nếu click nằm trong vùng nội dung
            content_rect = pygame.Rect(inner_x, inner_y, inner_w, inner_h)
            if content_rect.collidepoint(mx, my):
                for i, algo in enumerate(self.algos):
                    y_item = inner_y - self.scroll_y + i * self.item_h
                    r = pygame.Rect(inner_x, y_item, list_w, self.item_h - 6)
                    if r.collidepoint(mx, my):
                        self.selected_algo = algo
                        break

            # bắt đầu kéo scrollbar nếu bấm vào thumb
            if self._thumb_rect and self._thumb_rect.collidepoint(mx, my):
                self._dragging_bar = True
                self._drag_offset = my - self._thumb_rect.y
                return None

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging_bar = False
            return None

        if event.type == pygame.MOUSEMOTION and self._dragging_bar:
            # kéo thanh cuộn
            inner_y = self.right_rect.y + 10
            inner_h = self.right_rect.h - 20
            content_h = len(self.algos) * self.item_h
            max_scroll = max(0, content_h - inner_h)
            if max_scroll > 0 and self._thumb_rect:
                thumb_h = self._thumb_rect.h
                # vị trí thumb mới theo chuột (giới hạn trong track)
                track_top = inner_y
                track_bot = inner_y + inner_h - thumb_h
                new_thumb_y = max(track_top, min(event.pos[1] - self._drag_offset, track_bot))
                # map ngược ra scroll_y
                ratio = 0 if inner_h == thumb_h else (new_thumb_y - track_top) / (inner_h - thumb_h)
                self.scroll_y = int(ratio * max_scroll)
            return None

        return None
