import os
import pygame
import config as cfg
from model.board import Board

def load_image(file_name: str) -> pygame.Surface:
    path = os.path.join(cfg.IMAGES_DIR, file_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file {file_name} not found in {cfg.IMAGES_DIR}")
    return pygame.image.load(path)

def select_board(index: int) -> Board:
    board_path = os.path.join(cfg.BOARDS_DIR, f"board{index}.csv")
    return Board.from_csv(board_path)

def init_audio() -> tuple[pygame.mixer.Sound, pygame.mixer.Sound]:
    """Trả về (click_sound, error_sound). Nhạc nền sẽ chạy vòng lặp."""
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(cfg.SOUNDS_DIR, 'GameMusic.mp3'))
    pygame.mixer.music.play(-1)
    click_sound = pygame.mixer.Sound(os.path.join(cfg.SOUNDS_DIR, 'EnterSound.mp3'))
    error_sound = pygame.mixer.Sound(os.path.join(cfg.SOUNDS_DIR, 'error.mp3'))
    return click_sound, error_sound

def load_vehicle_images() -> dict:
    """Load & scale toàn bộ sprite xe, trả về dict để dùng khi vẽ."""
    car_s_img = load_image('Car_H1.png')  # xe của người chơi (id=0), dài 2, nằm ngang

    car_h_img = [load_image(f'Car_H{i}.png') for i in range(2, 6)]
    car_v_img = [load_image(f'Car_V{i}.png') for i in range(1, 6)]
    truck_h_img = [load_image(f'Truck_H{i}.png') for i in range(1, 4)]
    truck_v_img = [load_image(f'Truck_V{i}.png') for i in range(1, 4)]

    car_s_img = pygame.transform.scale(car_s_img, (cfg.CELL_WIDTH * 2, cfg.CELL_HEIGHT))
    car_h_img = [pygame.transform.scale(im, (cfg.CELL_WIDTH * 2, cfg.CELL_HEIGHT)) for im in car_h_img]
    car_v_img = [pygame.transform.scale(im, (cfg.CELL_WIDTH, cfg.CELL_HEIGHT * 2)) for im in car_v_img]
    truck_h_img = [pygame.transform.scale(im, (cfg.CELL_WIDTH * 3, cfg.CELL_HEIGHT)) for im in truck_h_img]
    truck_v_img = [pygame.transform.scale(im, (cfg.CELL_WIDTH, cfg.CELL_HEIGHT * 3)) for im in truck_v_img]

    return {
        "car_s_img": car_s_img,
        "car_h_img": car_h_img,
        "car_v_img": car_v_img,
        "truck_h_img": truck_h_img,
        "truck_v_img": truck_v_img,
    }
