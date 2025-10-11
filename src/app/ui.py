import pygame
import config as cfg

def show_image(screen: pygame.Surface, file_name: str,
               size=(cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT), position=(0, 0)):
    surf = pygame.image.load((cfg.IMAGES_DIR / file_name).as_posix() if hasattr(cfg, "IMAGES_DIR") and not isinstance(cfg.IMAGES_DIR, str)
                             else f"{cfg.IMAGES_DIR}/{file_name}")
    surf = pygame.transform.scale(surf, size)
    screen.blit(surf, position)

def show_text(screen: pygame.Surface, text: str, font_size: int, color: tuple, position: tuple):
    try:
        font = pygame.font.SysFont('comicsansms', font_size, bold=True)
    except:
        font = pygame.font.Font(None, font_size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=position)
    screen.blit(surf, rect)

def show_board(screen: pygame.Surface, board, images: dict, selected_vid=None):
    """Vẽ bàn cờ + xe; nếu selected_vid != None sẽ highlight xe được chọn."""
    board_matrix = board.to_matrix()

    # lưới
    for row in range(board.width):
        for col in range(board.width):
            rect = pygame.Rect(
                cfg.BOARD_X + col * cfg.CELL_WIDTH,
                cfg.BOARD_Y + row * cfg.CELL_HEIGHT,
                cfg.CELL_WIDTH,
                cfg.CELL_HEIGHT
            )
            pygame.draw.rect(screen, cfg.COLOR_BLACK, rect, width=1)

    # gom cell theo vehicle id
    vehicle_info = {}
    for r in range(board.width):
        for c in range(board.width):
            vid = board_matrix[r][c]
            if vid == -1:
                continue
            vehicle_info.setdefault(vid, {'cells': []})['cells'].append((r, c))

    for vid, info in vehicle_info.items():
        cells = info['cells']
        if not cells:
            continue
        rows = [rc[0] for rc in cells]
        cols = [rc[1] for rc in cells]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        orientation = 'H' if min_row == max_row else 'V'
        length = (max_col - min_col + 1) if orientation == 'H' else (max_row - min_row + 1)

        # chọn sprite
        if vid == 0:
            img = images["car_s_img"]
        else:
            if length == 2:
                if orientation == 'H':
                    lst = images["car_h_img"]
                else:
                    lst = images["car_v_img"]
            else:
                if orientation == 'H':
                    lst = images["truck_h_img"]
                else:
                    lst = images["truck_v_img"]
            img = lst[vid % len(lst)] if len(lst) else images["car_s_img"]

        pos = (cfg.BOARD_X + min_col * cfg.CELL_WIDTH, cfg.BOARD_Y + min_row * cfg.CELL_HEIGHT)
        screen.blit(img, pos)

        # highlight xe được chọn
        if selected_vid is not None and vid == selected_vid:
            rect = pygame.Rect(
                cfg.BOARD_X + min_col * cfg.CELL_WIDTH,
                cfg.BOARD_Y + min_row * cfg.CELL_HEIGHT,
                (max_col - min_col + 1) * cfg.CELL_WIDTH,
                (max_row - min_row + 1) * cfg.CELL_HEIGHT,
            )
            pygame.draw.rect(screen, cfg.COLOR_BRIGHT_GREEN, rect, width=3)

    show_text(screen, "Your Car", 24, cfg.COLOR_BRIGHT_BLUE, (90, 420))
    screen.blit(images["car_s_img"], (5, 450))
