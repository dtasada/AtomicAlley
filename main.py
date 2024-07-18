#!/usr/bin/env python3

import sys
from typing import Dict
import pygame
import itertools
from src.engine import *

# from src.player import *
from pathlib import Path


clock = pygame.time.Clock()
game = Game()
# player = Player()

tiles = [
    pygame.transform.scale_by(
        pygame.image.load(Path("resources", "images", "empty.png")), R
    ),
    pygame.transform.scale_by(
        pygame.image.load(Path("resources", "images", "tile.png")), R
    ),
]


class World:
    def __init__(self):
        self.data = dict.fromkeys(itertools.product(range(10), range(10)), 1)


world = World()


def main():
    buttons: Dict[str, Button] = {
        "b": ButtonToggle((100, 100), (24, 24), "toggle", 10),
        "title": ButtonLabel(
            (200, 200), 20, "BOTH", lambda: game.set_state(States.PLAY)
        ),
    }

    while game.running:
        for event in pygame.event.get():
            for button in buttons.values():
                button.process_event(event)

            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                case pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                        if game.state == States.PLAY:
                            game.set_state(States.MENU)
                        elif game.state == States.PLAY:
                            game.set_state(States.MENU)

        display.fill(Colors.LIGHT_GRAY)

        for pos, tile in world.data.items():
            x, y = pos
            # minimap
            mm_x = x * MMS
            mm_y = y * MMS
            pygame.draw.rect(display, (106, 190, 48), (mm_x, mm_y, MMS, MMS))
            pygame.draw.rect(display, WHITE, (mm_x, mm_y, MMS, MMS), 1)
            blit_x, blit_y = cart_to_iso(x, y, 0)
            # map
            display.blit(tiles[tile], (blit_x, blit_y))

        player.update()
        for button in buttons.values():
            button.update()

        pygame.display.update()
        clock.tick(game.target_fps)


if __name__ == "__main__":
    main()
