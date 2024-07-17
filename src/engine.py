import pygame
from math import sqrt


BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
WHITE = (255, 255, 255)

WIDTH, HEIGHT = 1280, 720
MMS = 15
R = 3
S = 31 * R
HS = 15 * R
QS = 8 * R
ORIGIN = (600, 60)

display = pygame.display.set_mode((WIDTH, HEIGHT))


def cart_to_iso(x, y, z):
    blit_x = ORIGIN[0] + x * HS - y * HS
    blit_y = ORIGIN[1] + x * QS + y * QS - z * HS
    return (blit_x, blit_y)

class Game:
    def __init__(self) -> None:
        self.running = True
        self.target_fps = 60
