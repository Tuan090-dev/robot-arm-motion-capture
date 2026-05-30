import pygame
import numpy as np
# Kích thước cửa sổ Pygame
BACKGROUND = (214, 214, 214)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BACKGROUND_PANEL = (249, 255, 230)

print('UI running')

def Draw_panel(screen):
    screen.fill(BACKGROUND)
    pygame.draw.rect(screen, GREEN, (50, 50, 650, 490))
    pygame.draw.rect(screen, BACKGROUND_PANEL, (55, 55, 640, 480))

    # Panel
    pygame.draw.rect(screen, GREEN, (750, 50, 650, 490))
    pygame.draw.rect(screen, BACKGROUND_PANEL, (755, 55, 640, 480))

def Show_cam(screen,frame, pos):
    frame_surface = pygame.surfarray.make_surface(np.transpose(frame, (1, 0, 2)))
    screen.blit(frame_surface, pos)

def Put_text(screen, font, text, pos):
    text_surface = font.render(text, True, (255, 0, 0))
    screen.blit(text_surface, pos)

def Put_texts(screen, font, texts, text_pos):
    for i in range(len(texts)):
        Put_text(screen, font, texts[i], text_pos[i])