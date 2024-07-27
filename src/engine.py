import pygame
import pygame.gfxdraw

from math import sqrt, floor
from random import randint as rand
from pathlib import Path
from enum import Enum
from typing import Any, Tuple
from pathlib import Path
from random import randint as rand, uniform as randf, choice

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
MMS = 1
HMMS = MMS / 2
QMMS = MMS / 4
R = 3
S = 32 * R
SR = S * R
HS = S / 2
QS = S / 4
ORIGIN = (0, 0)

# UI
BORDER_RADIUS = 8
ANTI_ALIASING = True

all_shadows = []

# Init
pygame.init()

#sfx
buzzing_channel = pygame.mixer.find_channel()
light_buzz = pygame.mixer.Sound(Path("resources", "sfx", "buzz.wav"))

fonts = [
    pygame.font.Font(Path("resources", "fonts", "Chicago.ttf"), i) for i in range(101)
]
underlines = [
    pygame.image.load(Path("resources", "images", "underlines.png")).subsurface(
        0, i * 83 + 14, 500, 83 - 14
    )
    for i in range(6)
]


def darken(img, m):
    ret = img.copy()
    black = pygame.Surface(img.size).convert_alpha()
    black.fill(Colors.BLACK)
    black.set_alpha(m * 255)
    img.blit(black, (0, 0))
    ret.blit(black, (0, 0))
    return ret


def cart_dir_to_vel(
    left,
    right,
    top,
    bottom,
    topleft=False,
    topright=False,
    bottomright=False,
    bottomleft=False,
    m=1,
):
    # TODO: Collision w/ objects
    # TODO: it's not handled here
    xvel, yvel, it = 0, 0, None
    if topleft:
        top = left = True
    if topright:
        top = right = True
    if bottomright:
        bottom = right = True
    if bottomleft:
        bottom = left = True
    if top:
        if left:
            xvel = -m
            it = "topleft"
        elif right:
            yvel = -m
            it = "topright"
        else:
            xvel = -m * sqrt(0.5)
            yvel = -m * sqrt(0.5)
            it = "top"
    elif bottom:
        if left:
            yvel = m
            it = "bottomleft"
        elif right:
            xvel = m
            it = "bottomright"
        else:
            xvel = m * sqrt(0.5)
            yvel = m * sqrt(0.5)
            it = "bottom"
    elif left:
        xvel = -m * sqrt(0.5)
        yvel = m * sqrt(0.5)
        it = "left"
    elif right:
        xvel = m * sqrt(0.5)
        yvel = -m * sqrt(0.5)
        it = "right"
    return xvel, yvel, it


def sign(n):
    if n > 0:
        return 1
    if n < 0:
        return -1
    return 0


def write(display, orientation, text, font, color, x, y):
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


def to_shadow(img):
    return pygame.mask.from_surface(img).to_surface(
        setcolor=Colors.BLACK, unsetcolor=None
    )


def cart_to_iso(x, y, z):
    blit_x = ORIGIN[0] + x * HS - y * HS
    blit_y = ORIGIN[1] + x * QS + y * QS - z * HS
    return (blit_x, blit_y)


def cart_to_mm(x, y, z):
    blit_x = x * MMS
    blit_y = y * MMS
    return (blit_x, blit_y)


def imgload(*path_, columns=1, scale=R, row=0, rows=1, start_frame=0, frames=0):
    image = pygame.transform.scale_by(
        pygame.image.load(Path(*path_)).convert_alpha(), scale
    )
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
    def __init__(self):
        self.running = True
        self.target_fps = 60
        self.state = States.MAIN_MENU
        self.fake_scroll = [0, 0]
        self.scroll = [0, 0]
        self.dialogue = None
        self.focus: Any = None

    def set_state(self, target_state):
        global buzzing_channel

        if target_state == States.MAIN_MENU:
            buzzing_channel.set_volume(0.7)
            buzzing_channel.play(light_buzz, -1)

            pygame.mixer.music.unload()
            pygame.mixer.music.load(Music.MAIN_MENU)
            pygame.mixer_music.play(-1)

        if self.state == States.MAIN_MENU and target_state == States.PLAY:
            buzzing_channel.stop()
            pygame.mixer.music.unload()

        self.state = target_state


class Music():
    MAIN_MENU = Path("resources", "sfx", "MainMenuMusic.mp3")


class States(Enum):
    MENU = 0
    SETTINGS = 1
    PLAY = 2
    WORKBENCH = 3
    MAIN_MENU = 4


class FontSize:
    SMALL = 28
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
display = pygame.display.set_mode((1280, 720))
game = Game()


class World:
    def __init__(self):
        self.data = {}
        # keys = [x + (0,) for x in itertools.product(range(20), range(20))]
        # left_wall = [(0, y, z) for y in range(20) for z in range(10)]
        # right_wall = [(x, 0, z) for x in range(20) for z in range(10)]
        # map_ = keys + left_wall + right_wall
        map_ = []
        self.data[(2, 2, 0)] = 1


world = World()
max_level = 5


class Node:
    def __init__(self, border):
        self.border = border
        self.left = None
        self.right = None
        self.level = 0
        self.color = [rand(0, 255) for _ in range(3)]

    def __str__(self):
        return f"Node[{self.level}][{self.x}, {self.y}, {self.w}, {self.h}]"

    @property
    def x(self):
        return self.border[0]

    @property
    def y(self):
        return self.border[1]

    @property
    def w(self):
        return self.border[2]

    @property
    def h(self):
        return self.border[3]

    @property
    def center(self):
        return [int(self.x + self.w / 2), int(self.y + self.h / 2)]

    def get_leaves(self):
        if self.left is None and self.right is None:
            yield self
        if self.left is not None:
            for leaf in self.left.get_leaves():
                yield leaf
        if self.right is not None:
            for leaf in self.right.get_leaves():
                yield leaf

    def draw_paths(self):
        if self.left is None or self.right is None:
            return
        pygame.draw.line(display, Colors.BLACK, self.left.center, self.right.center, 4)
        corridors.append([self.left.center, self.right.center])
        self.left.draw_paths()
        self.right.draw_paths()

    def split(self, level):
        self.level = level + 1
        if self.level == max_level:
            p = 0.3
            topleft = (
                rand(self.x + 1, self.x + int(self.w * p)),
                rand(self.y + 1, self.y + int(self.h * p)),
            )
            bottomright = (
                rand(self.x + 1 + int(self.w * (1 - p)), self.x + self.w),
                rand(self.y + 1 + int(self.h * (1 - p)), self.y + self.h),
            )
            w = bottomright[0] - topleft[0]
            h = bottomright[1] - topleft[1]
            self.room = [*topleft, w, h]
            return
        cur_level = self.level
        if rand(0, 1) == 0:
            # horizontal split
            height = int(rand(int(self.h * 0.3), int(self.h * 0.7)))
            self.left = Node([self.x, self.y, self.w, height])
            self.right = Node([self.x, self.y + height, self.w, self.h - height])
            if self.left.h / self.left.w < 0.45 or self.right.h / self.right.w < 0.45:
                self.split(cur_level - 1)
                return
            self.left.split(cur_level)
            self.right.split(cur_level)
        else:
            # vertical split
            width = int(rand(int(self.w * 0.3), int(self.w * 0.7)))
            self.left = Node([self.x, self.y, width, self.h])
            self.right = Node([self.x + width, self.y, self.w - width, self.h])
            if self.left.w / self.left.h < 0.45 or self.right.w / self.right.h < 0.45:
                self.split(cur_level - 1)
                return
            self.left.split(cur_level)
            self.right.split(cur_level)


corridors = []
