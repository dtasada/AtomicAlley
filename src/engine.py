from types import LambdaType
from typing import Tuple
import pygame


# Types
v2 = Tuple[float, float]

# Constants
WHITE = pygame.Color("white")

# Init
pygame.init()
fonts = [pygame.font.Font("resources/fonts/Chicago.ttf", i) for i in range(101)]


class ButtonLabel:
    def __init__(self, pos: Tuple, size: Tuple, text, do: LambdaType) -> None:
        # self.surf = pygame.image.load("resources/images/button.png")
        self.surf = pygame.surface.Surface((10, 10))
        self.surf.fill(pygame.Color("white"))
        self.rect = pygame.Rect(*pos, *size)
        self.text = text
        self.do = do

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.enabled = not self.enabled

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.do()

        display.blit(self.surf, self.rect)


class ButtonToggle:
    def __init__(
        self, pos: v2, size: v2, text, text_offset: int, enabled=False
    ) -> None:
        # self.surf = pygame.image.load("resources/images/button.png")
        self.button_surf = pygame.surface.Surface(size)
        self.button_surf.fill(WHITE)
        self.button_rect = pygame.Rect(*pos, *size)
        self.enabled = enabled
        self.text = fonts[self.button_rect.width].render(text, True, WHITE)
        self.text_rect = pygame.Rect(
            self.button_rect.right + text_offset,
            self.button_rect.top - 4,
            *self.text.get_size()  # - 4 is to compensate font vertical padding
        )

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
        pygame.draw.rect(display, WHITE, self.button_rect, width=1, border_radius=8)

        display.blit(self.text, self.text_rect)
        if self.enabled:
            pygame.draw.rect(display, WHITE, self.button_rect, border_radius=8)


class Game:
    def __init__(self) -> None:
        self.running = True
        self.target_fps = 60


# Globals
clock = pygame.time.Clock()
display = pygame.display.set_mode((1280, 720))
game = Game()
