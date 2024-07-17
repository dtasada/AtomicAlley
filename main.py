#!/usr/bin/env python3

import sys
import pygame
import itertools
from src.engine import *
from src.player import *
from pathlib import Path


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

        display.fill(Colors.LIGHT_GRAY)

        for pos, tile in world.data.items():
            x, y = pos
            # minimap
            mm_x = x * MMS
            mm_y = y * MMS
            pygame.draw.rect(display, (106, 190, 48), (mm_x, mm_y, MMS, MMS))
<<<<<<< HEAD
            pygame.draw.rect(display, WHITE, (mm_x, mm_y, MMS, MMS), 1)
            blit_x, blit_y = cart_to_iso(x, y, 0)
            # display.blit(pygame.font.SysFont("Times New Roman", 14).render(f"{x},{y}", True, BLACK), (blit_x, blit_y))
=======
            pygame.draw.rect(display, Colors.WHITE, (mm_x, mm_y, MMS, MMS), 1)
            blit_x = ORIGIN[0] + x * HS - y * HS
            blit_y = ORIGIN[1] + x * QS + y * QS
>>>>>>> 6c1f95607344bbb8ca5fd42c00ad8ff9e4eec9d4
            # map
            display.blit(tiles[tile], (blit_x, blit_y))

        player.update()
        b.update()
        title.update()

        pygame.display.update()
        clock.tick(game.target_fps)


if __name__ == "__main__":
    main()
