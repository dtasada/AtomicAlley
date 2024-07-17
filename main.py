#!/usr/bin/env python3

import pygame
from src.engine import *
from src.player import *
import sys
from pathlib import Path
import itertools


clock = pygame.time.Clock()
game = Game()
player = Player()

tiles = [
    pygame.transform.scale_by(pygame.image.load(Path("assets", "empty.png")), R),
    pygame.transform.scale_by(pygame.image.load(Path("assets", "tile.png")), R),
]


class World:
    def __init__(self):
        self.data = dict.fromkeys(itertools.product(range(10), range(10)), 1)


world = World()


# test_font = pygame.font.Font("path/font.ttf")
def main():
    b = ButtonToggle((100, 100), (24, 24), "toggle", 10)
    title = ButtonLabel((200, 200), 20, "BOTH", lambda: game.set_state(States.PLAY))

    while game.running:
        for event in pygame.event.get():
            b.process_event(event)
            title.process_event(event)

            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        display.fill((0, 0, 0))

        b.update()
        title.update()


def main():
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        display.fill(Colors.LIGHT_GRAY)

        for pos, tile in world.data.items():
            x, y = pos
            # minimap
            mm_x = x * MMS
            mm_y = y * MMS
            pygame.draw.rect(display, (106, 190, 48), (mm_x, mm_y, MMS, MMS))
            pygame.draw.rect(display, WHITE, (mm_x, mm_y, MMS, MMS), 1)
            blit_x = ORIGIN[0] + x * HS - y * HS
            blit_y = ORIGIN[1] + x * QS + y * QS
            # map
            display.blit(tiles[tile], (blit_x, blit_y))

        player.update()

        pygame.display.update()
        clock.tick(game.target_fps)


if __name__ == "__main__":
    main()
