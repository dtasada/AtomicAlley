import pygame
from pygame.time import get_ticks as ticks
from math import sqrt, floor, atan2, cos, sin, pi
from random import randint as rand
from pathlib import Path
from enum import Enum
from typing import Any, List, Tuple
from pathlib import Path
from random import randint as rand, uniform as randf, choice
import random
from pprint import pprint


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


def v2_center(v) -> v2:
    return [s / 2 for s in v]


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

# sfx
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
    black = pygame.Surface(img.get_size()).convert_alpha()
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
    # TODO: nope it's not handled here
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


def imgload(
    *path_, columns=1, rows=1, scale=R
) -> pygame.Surface | List[pygame.Surface] | List[List[pygame.Surface]]:
    image = pygame.transform.scale_by(
        pygame.image.load(Path(*path_)).convert_alpha(), scale
    )

    if columns * rows == 1:  # if contains only one image
        return image
    else:
        frame_width = image.get_width() / columns
        frame_height = image.get_height() / rows

        ret = []
        if columns > 1 and rows == 1:  # if image is divided into columns
            for i in range(columns):
                sub = image.subsurface(
                    i * frame_width,
                    0,
                    frame_width,
                    frame_height,
                )
                ret.append(sub)

        elif rows > 1 and columns == 1:  # if image is divided into rows
            for i in range(rows):
                sub = image.subsurface(
                    0,
                    i * frame_height,
                    frame_width,
                    frame_height,
                )
                ret.append(sub)

        elif columns > 1 and rows > 1:  # if image is divided two-dimensinally
            ret: List[List[pygame.Surface]] = []
            for i in range(rows):
                row = image.subsurface(
                    0, i * frame_height, image.get_width(), frame_height
                )
                row_sheet = []
                for j in range(columns):
                    frame = row.subsurface(
                        j * frame_width,
                        0,
                        frame_width,
                        frame_height,
                    )
                    row_sheet.append(frame)

                ret.append(row_sheet)

        return ret


class Smart:
    @property
    def x(self):
        return self.mmrect.x / game.rect_scale

    @x.setter
    def x(self, value):
        self.mmrect.x = value * game.rect_scale

    @property
    def y(self):
        return self.mmrect.y / game.rect_scale
    
    @y.setter
    def y(self, value):
        self.mmrect.y = value * game.rect_scale


class Game:
    def __init__(self):
        self.running = True
        self.target_fps = 60
        self.state = States.MAIN_MENU
        self.fake_scroll = [0, 0]
        self.scroll = [0, 0]
        self.dialogue = None
        self.focus: Any = None
        self.late_events = []

        self.loading = False
        self.rect_scale = 20
        self.loading_progress = 0.0
        self.progress_bar_images = imgload(
            "resources", "images", "menu", "loading.png", rows=11, scale=3
        )
        self.progress_bar_image = self.progress_bar_images[0]
        self.wall_height = 5
        self.screen_shake_offset = [0, 0]
        self.last_screen_shake = ticks()
        self.screen_shake_mult = 0
        self.screen_shake_duration = None
        
    def screen_shake(self, mult, dur):
        self.screen_shake_duration = dur
        self.screen_shake_mult = mult
        self.last_screen_shake = ticks()

    def set_state(self, target_state):
        global buzzing_channel

        if target_state == States.MAIN_MENU:
            buzzing_channel.set_volume(0.7)
            buzzing_channel.play(light_buzz, -1)

            pygame.mixer.music.unload()
            pygame.mixer.music.load(Music.MAIN_MENU)
            pygame.mixer.music.play(-1)

        if self.state == States.MAIN_MENU and target_state == States.PLAY:
            buzzing_channel.stop()
            pygame.mixer.music.fadeout(300)
            pygame.mixer.music.unload()

        self.state = target_state


class Music:
    MAIN_MENU = Path("resources", "sfx", "MainMenuMusic.mp3")


class States(Enum):
    MAIN_MENU = 0
    PLAY = 1
    SETTINGS = 2
    END = 3


class FontSize:
    SMALL = 28
    BODY = 36
    SUBTITLE = 40
    DIALOGUE = 42
    TITLE = 64

class Weapons(Enum):
    HANDS = 0
    BAT = 1

class Colors:
    BLACK = (0, 0, 0)
    LIGHT_GRAY = (200, 200, 200)
    GRAYS = [(x, x, x) for x in range(255)]
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)


# Globals
clock = pygame.time.Clock()
pygame.display.set_caption("Atomic Alley")
window = pygame.display.set_mode((1280, 720), vsync=1)
display = pygame.display.get_surface()
game = Game()
all_particles = []


class World:
    class Colors:
        BLACK = 0
        WHITE = 1
        GRAY = 2
        RGB = 3

    def __init__(self):
        self.data = {}
        self.interactives = {}
        self.enemies = {}
        self.late_interactives = []
        self.already_interacted = False
        self.late_enemies = []

    def try_modifying(self, data, check_higher=False):
        targ_pos, value = data
        for data in self.data:
            # data = ((x, y, z), value)
            if data[0] == targ_pos or (check_higher and data[0][:2] == targ_pos[:2]):
                return False
        else:
            self.data.append((targ_pos, value))
            return True


world = World()
max_level = 5


class RoomType(Enum):
    NORMAL = 0
    BAR = 1


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

    def set_room_type(self):
        room_type = rand(1, 10)
        if room_type == 1:
            self.room_type = RoomType.BAR
        else:
            self.room_type = RoomType.NORMAL
            self.has_chest = True
            try:
                self.chest_offset = (
                    rand(1, self.room[2] - 1 - game.wall_height),
                    rand(1, self.room[3] - 1 - game.wall_height),
                )
            except ValueError:
                self.has_chest = False

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
            self.set_room_type()
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


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = rand(3, 6)
        self.yvel = randf(-4, -5)
        self.xvel = randf(-1.3, 1.3)
        self.color = [rand(30, 50)] * 3
        self.last_spawn = ticks()

    def update(self):
        self.x += self.xvel
        self.yvel += 0.5
        self.y += self.yvel
        if ticks() - self.last_spawn >= 270:
            all_particles.remove(self)


corridors = []
