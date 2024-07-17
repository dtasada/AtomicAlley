import pygame


BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
WHITE = (255, 255, 255)


WIDTH, HEIGHT = 1280, 720
MMS = 15
R = 3
S = 31 * R
HS = 15 * R
QS = 8 * R
ORIGIN = (500, 30)

display = pygame.display.set_mode((WIDTH, HEIGHT))

class Game:
    def __init__(self) -> None:
        self.running = True
        self.target_fps = 60
