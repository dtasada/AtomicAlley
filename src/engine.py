import random
import sys
import pygame
import itertools

import pygame.gfxdraw
from pygame.time import get_ticks as ticks
import time
from enum import Enum
from types import LambdaType
from typing import Tuple
from pathlib import Path
from math import floor, sqrt
from random import randint as rand, uniform as randf, choice

from math import floor, sqrt
from random import randint as rand



# Types
v2 = Tuple[float, float]


def v2_add(a, b) -> v2:
    return (a[0] + b[0], a[1] + b[1])


def v2_sub(a, b) -> v2:
    return (a[0] - b[0], a[1] - b[1])


def v2_len(v) -> float:
    return sqrt(v[0] ** 2 + v[1] ** 2)


# Constants
WIDTH, HEIGHT = 1280, 720
MMS = 1
HMMS = MMS / 2
QMMS = MMS / 4
R = 3
S = 32 * R
SR = S * R
HS = S / 2
QS = S / 4
ORIGIN = (0, 0)

BORDER_RADIUS = 8
ANTI_ALIASING = True

all_shadows = []

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


def darken(img, m):
    ret = img.copy()
    black = pygame.Surface(img.size).convert_alpha()
    black.fill(Colors.BLACK)
    black.set_alpha(m * 255)
    img.blit(black, (0, 0))
    ret.blit(black, (0, 0))
    return ret


def cart_dir_to_vel(left, right, top, bottom, topleft=False, topright=False, bottomright=False, bottomleft=False, m=1):
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
    return pygame.mask.from_surface(img).to_surface(setcolor=Colors.BLACK, unsetcolor=None)


def cart_to_iso(x, y, z):
    blit_x = ORIGIN[0] + x * HS - y * HS
    blit_y = ORIGIN[1] + x * QS + y * QS - z * HS
    return (blit_x, blit_y)


def cart_to_mm(x, y, z):
    blit_x = x * MMS
    blit_y = y * MMS
    return (blit_x, blit_y)


def imgload(*path_, columns=1, scale=R, row=0, rows=1, start_frame = 0, frames = 0):
    image = pygame.transform.scale_by(pygame.image.load(Path(*path_)).convert_alpha(), scale)
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


class TextWriter:
    def __init__(
        self, content, pos, font_size, color, anchor="topleft", writer_speed=0.25
    ):
        self.index = 0.0
        self.show = True
        self.writer_speed = writer_speed
        self.font_size = font_size
        self.body_pos = pos
        self.body_texs = [
            fonts[font_size].render(
                content[:i] + "_" if i < len(content) else content[:i], False, color
            )
            for i in range(len(content) + 1)
        ]
        self.body_rects = [
            self.body_texs[i].get_rect() for i in range(len(self.body_texs))
        ]
        [setattr(br, anchor, pos) for br in self.body_rects]

    def start(self):
        self.show = True

    def kill(self):
        self.index = 0
        self.show = False

    def update(self):
        if pygame.key.get_just_pressed()[pygame.K_SPACE]:
            if self.index < len(self.body_texs) - 1:
                self.index = len(self.body_texs) - 1
            else:
                self.kill()

        display.blit(
            self.body_texs[floor(self.index)], self.body_rects[floor(self.index)]
        )
        # rounding bc floating point bs (apparently 0.0 + 0.1 = 0.100000000096)
        target = self.index + self.writer_speed
        if target <= len(self.body_texs) - 1:
            self.index = target


class Dialogue(TextWriter):
    def __init__(self, content, speaker):
        self.margin = 16
        self.back_color = Colors.GRAYS[32]
        self.body_color = Colors.WHITE
        self.speaker = speaker  # speaker is the character that says the thing
        size = (display.get_width() - self.margin * 2, 320)
        self.master_rect = pygame.Rect(
            (self.margin, display.get_height() - size[1] - self.margin),
            size,
        )
        self.speaker_tex = fonts[FontSize.SUBTITLE].render(
            self.speaker, ANTI_ALIASING, self.body_color
        )
        self.speaker_rect = self.speaker_tex.get_rect(
            topleft=(
                self.margin * 2,
                display.get_height() - self.master_rect.height - self.margin / 2,
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
        if self.show:
            pygame.draw.rect(
                display, self.back_color, self.master_rect, border_radius=BORDER_RADIUS
            )  # render box
            display.blit(self.speaker_tex, self.speaker_rect)  # render speaker
            super().update()  # render body


class Interactive:
    DIALOGUE = 0
    MUT_PLAYER = 1

    def __init__(self, tex_path, pos: v2, do, dialogues=None):
        self.tex = pygame.transform.scale_by(
            pygame.image.load(tex_path).convert_alpha(), R
        )
        self.rect = self.tex.get_rect()
        self.do = do
        self.pos = pos  # world pos, not blit pos
        self.prompt = TextWriter(
            "Press <e> to interact",
            (display.width / 2, display.height * 2 / 3),
            FontSize.BODY,
            Colors.WHITE,
            anchor="center",
            writer_speed=1.5,
        )
        self.dialogues = dialogues
        if self.dialogues and self.do != Interactive.DIALOGUE:
            print("Interactive object has type of DIALOGUE but no given dialogues")
            sys.exit(1)

    def update(self, player):
        self.rect.topleft = v2_sub(cart_to_iso(*self.pos, 0), game.scroll)
        display.blit(self.tex, self.rect)

        if v2_len((player.x - self.pos[0], player.y - self.pos[1])) <= 3:
            self.prompt.start()
            self.prompt.update()

            if pygame.key.get_just_pressed()[pygame.K_e]:
                if self.do == Interactive.DIALOGUE:
                    game.dialogue = self.dialogues[0]
                    game.dialogue.start()
        else:
            self.prompt.kill()


class Game:
    def __init__(self) -> None:
        self.running = True
        self.target_fps = 60
        self.state = States.PLAY
        self.fake_scroll = [0, 0]
        self.scroll = [0, 0]
        self.dialogue = None

    def set_state(self, target_state):
        self.state = target_state

    def set_dialogue(self, dialogue: Dialogue):
        self.dialogue = dialogue


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
        return [self.x + self.w / 2, self.y + self.h / 2]

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
        self.left.draw_paths()
        self.right.draw_paths()
    
    def split(self, level):
        self.level = level + 1
        if self.level == 5:
            p = 0.3
            topleft = (rand(self.x + 1, self.x + int(self.w * p)), rand(self.y + 1, self.y + int(self.h * p)))
            bottomright = (rand(self.x + 1 + int(self.w * (1 - p)), self.x + self.w), rand(self.y + 1 + int(self.h * (1 - p)), self.y + self.h))
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
        

def pg_to_pil(pg_img):
    return PIL.Image.frombytes("RGBA", pg_img.get_size(), pygame.image.tobytes(pg_img, "RGBA"))



