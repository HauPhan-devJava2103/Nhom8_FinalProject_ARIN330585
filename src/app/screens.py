import pygame
import config as cfg
from .ui import show_image, show_text

def start_screen(screen: pygame.Surface, click_sound, sound_on: bool) -> tuple[str, bool]:
    """Trả về (signal, sound_on). signal = 'level' để sang màn chọn."""
    show_image(screen, 'StartGame.png')
    pygame.display.update()

    isStart = True
    signal = ""
    while isStart:
        mouse_pos = pygame.mouse.get_pos()
        show_image(screen, 'sound.png' if sound_on else 'noSound.png',
                   (cfg.BUTTON_TOOL, cfg.BUTTON_TOOL), (820, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sound_rect = pygame.Rect(820, 10, cfg.BUTTON_TOOL, cfg.BUTTON_TOOL)
                start_rect = pygame.Rect(cfg.WINDOW_WIDTH // 2 - 140, cfg.WINDOW_HEIGHT // 2 + 195, 280, 90)
                if sound_rect.collidepoint(mouse_pos):
                    if sound_on: click_sound.play()
                    sound_on = not sound_on
                    pygame.mixer.music.unpause() if sound_on else pygame.mixer.music.pause()
                if start_rect.collidepoint(mouse_pos):
                    isStart = False
                    signal = "level"
        pygame.display.update()
    return signal, sound_on
