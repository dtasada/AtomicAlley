from .engine import *

from types import LambdaType

import random


class Button:
    def __init__(self, pos: v2, size: int, text) -> None:
        self.text = fonts[size].render(text, True, Colors.WHITE)
        self.text_rect = self.text.get_rect(topleft=pos)
        self.underline = pygame.transform.scale(
            random.choice(underlines),
            (self.text_rect.width, self.text_rect.width * 0.2),
        )
        self.underline_rect = self.underline.get_rect(
            topleft=(self.text_rect.left, self.text_rect.bottom)
        )

    def update(self):
        display.blit(self.text, self.text_rect)
        if self.text_rect.collidepoint(pygame.mouse.get_pos()):
            display.blit(self.underline, self.underline_rect)

    def process_event(self, event) -> None: ...


class ButtonLabel(Button):
    def __init__(self, pos: v2, font_size: int, text, do: LambdaType) -> None:
        super().__init__(pos, font_size, text)
        self.do = do

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.text_rect.collidepoint(pygame.mouse.get_pos()):
                self.do()


class ButtonToggle(Button):
    def __init__(self, pos: v2, size: int, text, text_offset: int, enabled=False):
        super().__init__(pos, size, text)

        self.button_surf = pygame.surface.Surface((size, size))
        self.button_surf.fill(Colors.WHITE)
        self.button_rect = pygame.Rect(pos, (size, size))

        self.underline_rect.left = self.button_rect.right + 8

        self.text_rect = pygame.Rect(
            self.button_rect.right + text_offset,
            self.button_rect.top - 4,  # - 4 is to compensate font vertical padding
            *self.text.get_size(),
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
            display,
            Colors.WHITE,
            self.button_rect,
            width=1,
            border_radius=BORDER_RADIUS,
        )

        super().update()

        if self.enabled:
            pygame.draw.rect(display, Colors.WHITE, self.button_rect, border_radius=8)

