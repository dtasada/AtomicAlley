import random
import sys
import pygame
import itertools

import pygame.gfxdraw
from pygame.math import Vector2

from enum import Enum
from types import LambdaType
from typing import Any, Tuple
from pathlib import Path

from math import acos, floor, sqrt
from random import randint as rand

BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
WHITE = (255, 255, 255)

# Types
v2 = Tuple[float, float]


def v2_add(a, b) -> v2:
    return (a[0] + b[0], a[1] + b[1])


def v2_sub(a, b) -> v2:
    return (a[0] - b[0], a[1] - b[1])


def v2_dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1]


def v2_len(v) -> float:
    return sqrt(v[0] ** 2 + v[1] ** 2)


# Constants
WIDTH, HEIGHT = 1280, 720
MMS = 16
R = 3
S = 32 * R
SR = S * R
HS = S / 2
QS = S / 4
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
        0, i * 83 + 14, 500, 83 - 14
    )
    for i in range(6)
]
tiles = [
    pygame.transform.scale_by(
        pygame.image.load(Path("resources", "images", "empty.png")), R
    ),
    pygame.transform.scale_by(
        pygame.image.load(Path("resources", "images", "tile.png")), R
    ),
]


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


def imgload(*path_, columns=1, scale=R, row=0, rows=1, start_frame=0, frames=0):
    image = pygame.transform.scale_by(pygame.image.load(Path(*path_)), scale)
    if frames > 0:
        ret = []
        width = image.get_width() / columns
        height = image.get_height() / rows
        for i in range(frames):
            sub = image.subsurface(
                start_frame * width + i * width, row * height, width, height
            )
            ret.append(sub)
        return ret
    return image


class Game:
    def __init__(self) -> None:
        self.running = True
        self.target_fps = 60
        self.state = States.PLAY
        self.fake_scroll = [0, 0]
        self.scroll = [0, 0]
        self.dialogue = None
        self.focus: Any = None

    def set_state(self, target_state):
        self.state = target_state


class World:
    def __init__(self):
        self.data = dict.fromkeys(itertools.product(range(10), range(10)), None)
        self.data = {k: rand(1, 1) for k, v in self.data.items()}


class States(Enum):
    MENU = 0
    SETTINGS = 1
    PLAY = 2
    WORKBENCH = 3


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
