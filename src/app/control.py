import pygame
import config as cfg

# Map phím sang ký tự hướng
DIR_KEYS = {
    pygame.K_LEFT: 'L', pygame.K_a: 'L',
    pygame.K_RIGHT: 'R', pygame.K_d: 'R',
    pygame.K_UP: 'U', pygame.K_w: 'U',
    pygame.K_DOWN: 'D', pygame.K_s: 'D',
}


def pixel_to_cell(px, py):
    """Chuyển tọa độ pixel thành ô (row, col) trên board. Trả về None nếu ngoài board."""
    if not (cfg.BOARD_X <= px < cfg.BOARD_X + cfg.BOARD_WIDTH and
            cfg.BOARD_Y <= py < cfg.BOARD_Y + cfg.BOARD_HEIGHT):
        return None
    col = (px - cfg.BOARD_X) // cfg.CELL_WIDTH
    row = (py - cfg.BOARD_Y) // cfg.CELL_HEIGHT
    return int(row), int(col)


def vid_at_mouse(board, mouse_pos):
    """Lấy id xe (vid) tại vị trí chuột. Nếu ngoài board trả về -1."""
    pos = pixel_to_cell(*mouse_pos)
    if pos is None:
        return -1
    r, c = pos
    return board.to_matrix()[r][c]


def _dir_of_move(board, move) -> str:
    """
    Suy ra ký tự hướng ('L','R','U','D') từ Move:
    - Nếu xe nằm ngang: move.move=+1 -> 'R', -1 -> 'L'
    - Nếu xe nằm dọc  : move.move=+1 -> 'D', -1 -> 'U'
    """
    mv = move[0] if (isinstance(move, (tuple, list)) and len(move) >= 1) else move
    v = board.vehicles[mv.vehicle_index]
    if v.horizontal:
        return 'R' if mv.move == 1 else 'L'
    else:
        return 'D' if mv.move == 1 else 'U'


def try_apply_move(board, selected_vid, dir_char):
    """
    Tìm một move trong board.get_moves() thuộc xe selected_vid & hướng dir_char,
    rồi áp dụng nó. Trả về (new_board, moved: bool, cost: int).
    """
    d = dir_char.upper()
    for item in board.get_moves():
        # item là (Move, cost)
        if isinstance(item, (tuple, list)) and len(item) == 2:
            mv, c = item
        else:
            mv, c = item, 0  # fallback an toàn

        if mv.vehicle_id != selected_vid:
            continue
        if _dir_of_move(board, mv) == d:
            return board.move_vehicle(move=mv), True, c
    return board, False, 0
