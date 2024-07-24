#!/usr/bin/env python3

import itertools
import pygame
import sys

from pathlib import Path
from typing import Dict

from src.engine import *
from src.player import *


clock = pygame.time.Clock()

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
        keys = [x + (0,) for x in itertools.product(range(10), range(10))]
        # keys.extend([
        #     (5, 5, 1)
        # ])
        self.data = dict.fromkeys(keys, None)
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
                    if event.key == pygame.K_ESCAPE:
                        if game.state == States.PLAY:
                            game.set_state(States.MENU)
                        elif game.state == States.PLAY:
                            game.set_state(States.MENU)

                    elif event.key == pygame.K_SPACE:
                        player.dash()

        display.fill(Colors.GRAYS[50])

        player.scroll()

        display.fill(Colors.GRAYS[50])

        for pos, tile in world.data.items():
            x, y, z = pos
            # minimap
            mm_x = x * MMS
            mm_y = y * MMS
            pygame.draw.rect(display, [255 - z / 10 * 255] * 3, (mm_x, mm_y, MMS, MMS))
            pygame.draw.rect(display, Colors.BLACK, (mm_x, mm_y, MMS, MMS), 1)
            if tile > 0:
                blit_x, blit_y = cart_to_iso(x, y, z)
                # map
                blit_x -= game.scroll[0]
                blit_y -= game.scroll[1]
                display.blit(tiles[tile], (blit_x, blit_y))

        for shadow in all_shadows:
            shadow.update()
        player.update()
        for button in buttons.values():
            button.update()
        
        write("topright", int(clock.get_fps()), fonts[25], Colors.GRAYS[200], WIDTH - 9, 5)
        if game.state == States.MENU:
            for button in buttons.values():
                button.update()

        # dg.update()

        pygame.display.update()
        clock.tick(game.target_fps)


if __name__ == "__main__":
    main()
