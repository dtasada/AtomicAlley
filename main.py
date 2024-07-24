#!/usr/bin/env python3

import itertools
import pygame
import sys

from pathlib import Path
from typing import Dict

from src.engine import *
from src.player import *


clock = pygame.time.Clock()
player = Player()

tiles = [
    pygame.transform.scale_by(
        pygame.image.load(Path("resources", "images", "empty.png")), R
    ),
    pygame.transform.scale_by(
        pygame.image.load(Path("resources", "images", "tile_g.png")), R
    ),
]


class World:
    def __init__(self):
        self.data = dict.fromkeys(itertools.product(range(10), range(10)), None)
        self.data = {k: rand(1, 1) for k, v in self.data.items()}


world = World()
surfs = [gen_char() for _ in range(20)]


def main():
    buttons: Dict[str, Button] = {
        "b": ButtonToggle((100, 100), 24, "toggle", 10),
        "title": ButtonLabel(
            (200, 200), 20, "BOTH", lambda: game.set_state(States.PLAY)
        ),
    }

    tw = TextWriter("Atomic Alley", (300, 300), FontSize.DIALOGUE, Colors.WHITE)
    dg = Dialogue("Wow this alley really is atomic!", "Dexter")

    while game.running:
        for event in pygame.event.get():
            if game.state == States.MENU:
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

        display.fill(Colors.GRAYS[50])

        player.scroll()

        display.fill(Colors.GRAYS[50])

        for pos, tile in world.data.items():
            x, y = pos
            # minimap
            mm_x = x * MMS
            mm_y = y * MMS
            # pygame.draw.rect(display, (106, 190, 48), (mm_x, mm_y, MMS, MMS))
            # pygame.draw.rect(display, WHITE, (mm_x, mm_y, MMS, MMS), 1)
            if tile > 0:
                blit_x, blit_y = cart_to_iso(x, y, 0)
                # display.blit(pygame.font.SysFont("Times New Roman", 14).render(f"{x},{y}", True, BLACK), (blit_x, blit_y))
                # map
                blit_x -= game.scroll[0]
                blit_y -= game.scroll[1]
                display.blit(tiles[tile], (blit_x, blit_y))

        player.update()
        for button in buttons.values():
            button.update()
        
        write("topleft", int(clock.get_fps()), fonts[25], Colors.GRAYS[200], 5, 5)
        if game.state == States.MENU:
            for button in buttons.values():
                button.update()

        dg.update()

        pygame.display.update()
        clock.tick(game.target_fps)


if __name__ == "__main__":
    main()
