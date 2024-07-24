import random
import pygame

import pygame.gfxdraw

from enum import Enum
from types import LambdaType
from typing import Tuple
from pathlib import Path

from math import floor
from random import randint as rand


BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
WHITE = (255, 255, 255)

# Types
v2 = Tuple[float, float]

# Constants
WIDTH, HEIGHT = 1280, 720
MMS = 16
R = 3
S = 32 * R
HS = 16 * R
QS = 8 * R
ORIGIN = (0, 0)

BORDER_RADIUS = 8
ANTI_ALIASING = True

# Init
pygame.init()
fonts = [
    pygame.font.Font(Path("resources", "fonts", "Chicago.ttf"), i) for i in range(101)
]
underlines = [
    pygame.image.load(Path("resources", "images", "underlines.png")).subsurface(
        0, i * 83, 500, 83
    )
    for i in range(6)
]


class Button:
    def __init__(self, pos: v2, size: int, text) -> None:
        # self.surf = pygame.image.load("resources/images/button.png")
        self.text = fonts[size].render(text, True, Colors.WHITE)
        self.text_rect = pygame.Rect(pos, self.text.get_size())
        self.underline = random.choice(underlines)
        self.underline_rect = pygame.Rect(
            pos[1], self.text_rect.bottom, self.text_rect.width, 24
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


def write(orientation, text, font, color, x, y):
    surf = font.render(str(text), True, color)
    rect = surf.get_rect()
    setattr(rect, orientation, (x, y))
    display.blit(surf, rect)


def gen_char():
    surf = pygame.Surface((10, 10), pygame.SRCALPHA)
    n = 0
    x = rand(0, 9)
    y = rand(0, 9)
    while n < 20:
        o = rand(1, 8)
        if o == 1:
            x += 1
            y -= 1
        elif o == 2:
            x += 1
        elif o == 3:
            x += 1
            y += 1
        elif o == 4:
            y += 1
        elif o == 5:
            x -= 1
            y += 1
        elif o == 6:
            x -= 1
        elif o == 7:
            x -= 1
            y -= 1
        elif o == 8:
            y -= 1
        surf.set_at((x, y), Colors.BLACK)
        n += 1
    surf = pygame.transform.scale_by(surf, 10)
    return surf


def cart_to_iso(x, y, z):
    blit_x = ORIGIN[0] + x * HS - y * HS
    blit_y = ORIGIN[1] + x * QS + y * QS - z * HS
    return (blit_x, blit_y)


def imgload(*path_, frames=1, vertical=False, scale=R):
    image = pygame.transform.scale_by(pygame.image.load(Path(*path_)), scale)
    if frames > 1:
        ret = []
        width = image.get_width() / frames
        height = image.get_height() / frames
        for i in range(frames):
            if vertical:
                sub = image.subsurface(0, i * height, image.get_width(), height)
            else:
                sub = image.subsurface(i * width, 0, image.get_height(), height)
            ret.append(sub)
        return ret
    return image


class TextWriter:
    def __init__(self, content, pos, font_size, color):
        self.index = 0.0
        self.font_size = font_size
        self.body_pos = pos
        self.body_texs = [
            fonts[font_size].render(content[:i], False, color)
            for i in range(len(content) + 1)
        ]
        self.body_rects = [
            self.body_texs[i].get_rect(topleft=pos) for i in range(len(self.body_texs))
        ]

    def update(self):
        display.blit(
            self.body_texs[floor(self.index)], self.body_rects[floor(self.index)]
        )
        # rounding bc floating point bs (apparently 0.0 + 0.1 = 0.100000000096)
        # shut the fuck up pussy
        target = self.index + 0.25
        if target <= len(self.body_texs) - 1:
            self.index = target


class Dialogue(TextWriter):
    def __init__(self, content, speaker):
        self.margin = 16
        self.back_color = Colors.GRAYS[32]
        self.body_color = Colors.WHITE
        self.speaker = speaker  # speaker is the character that says the thing
        size = (WIDTH - self.margin * 2, 240)
        self.master_rect = pygame.Rect(
            (self.margin, HEIGHT - size[1] - self.margin),
            size,
        )
        self.speaker_tex = fonts[FontSize.SUBTITLE].render(
            self.speaker, ANTI_ALIASING, self.body_color
        )
        self.speaker_rect = self.speaker_tex.get_rect(
            topleft=(
                self.margin * 2,
                HEIGHT - self.master_rect.height - self.margin / 2,
            )
        )
        super().__init__(  # careful not to overwrite anything here
            content,
            self.master_rect.topleft,
            FontSize.BODY,
            Colors.WHITE,
        )
        for rect in self.body_rects:
            rect.topleft = (
                rect.left + self.margin,
                self.speaker_rect.bottom + self.margin / 2,
            )

    def update(self):
        pygame.draw.rect(
            display, self.back_color, self.master_rect, border_radius=BORDER_RADIUS
        )  # render box
        display.blit(self.speaker_tex, self.speaker_rect)  # render speaker
        super().update()  # render body


class Game:
    def __init__(self) -> None:
        self.running = True
        self.target_fps = 60
        self.state = States.PLAY
        self.fake_scroll = [0, 0]
        self.scroll = [0, 0]

    def set_state(self, target_state):
        self.state = target_state


class States(Enum):
    MENU = 0
    SETTINGS = 1
    PLAY = 2


class FontSize:
    BODY = 36
    SUBTITLE = 40
    DIALOGUE = 42
    TITLE = 64


class Colors:
    BLACK = (0, 0, 0)
    LIGHT_GRAY = (200, 200, 200)
    GRAYS = [(x, x, x) for x in range(255)]
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)


# Globals
clock = pygame.time.Clock()
display = pygame.display.set_mode((WIDTH, HEIGHT))
game = Game()
