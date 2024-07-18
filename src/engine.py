from enum import Enum
from types import LambdaType
from typing import Tuple
import random
import pygame


# Types
v2 = Tuple[float, float]

# Constants
WIDTH, HEIGHT = 1280, 720
MMS = 15
R = 3
S = 31 * R
HS = 15 * R
QS = 8 * R
ORIGIN = (500, 30)


# Init
pygame.init()
fonts = [pygame.font.Font("resources/fonts/Chicago.ttf", i) for i in range(101)]
underlines = [
    pygame.image.load("resources/images/underlines.png").subsurface(0, i * 83, 500, 83)
    for i in range(6)
]


class Button:
    def __init__(self, pos: v2, size: int, text) -> None:
        # self.surf = pygame.image.load("resources/images/button.png")
        self.text = fonts[size].render(text, True, Colors.WHITE)
        self.text_rect = pygame.Rect(pos, self.text.size)
        self.underline = random.choice(underlines)
        self.underline_rect = pygame.Rect(
            pos[1], self.text_rect.bottom, self.text_rect.width, 24
        )

    def update(self):
        display.blit(self.text, self.text_rect)
        if self.text_rect.collidepoint(pygame.mouse.get_pos()):
            display.blit(self.underline, self.underline_rect)


class ButtonLabel(Button):
    def __init__(self, pos: v2, font_size: int, text, do: LambdaType) -> None:
        super().__init__(pos, font_size, text)
        self.do = do

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.text_rect.collidepoint(pygame.mouse.get_pos()):
                self.do()


class ButtonToggle(Button):
    def __init__(
        self, pos: v2, size: int, text, text_offset: int, enabled=False
    ) -> None:
        super().__init__(pos, size, text)

        self.button_surf = pygame.surface.Surface((size, size))
        self.button_surf.fill(Colors.WHITE)
        self.button_rect = pygame.Rect(pos, (size, size))

        self.text_rect = pygame.Rect(
            self.button_rect.right + text_offset,
            self.button_rect.top - 4,  # - 4 is to compensate font vertical padding
            *self.text.get_size()
        )

        self.enabled = enabled

        self.combi_rect = pygame.Rect(
            self.button_rect.left,
            self.button_rect.top,
            self.button_rect.width + text_offset + self.text_rect.width,
            self.button_rect.height,
        )

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.combi_rect.collidepoint(pygame.mouse.get_pos()):
                self.enabled = not self.enabled

    def update(self):
        pygame.draw.rect(
            display, Colors.WHITE, self.button_rect, width=1, border_radius=8
        )

        super().update()

        if self.enabled:
            pygame.draw.rect(display, Colors.WHITE, self.button_rect, border_radius=8)


class Game:
    def __init__(self) -> None:
        self.running = True
        self.target_fps = 60
        self.state = States.PLAY

    def set_state(self, target_state):
        self.state = target_state


class Colors:
    BLACK = (0, 0, 0)
    LIGHT_GRAY = (200, 200, 200)
    WHITE = (255, 255, 255)


class States(Enum):
    MENU = 0
    SETTINGS = 1
    PLAY = 2


# Globals
clock = pygame.time.Clock()
display = pygame.display.set_mode((WIDTH, HEIGHT))
game = Game()
