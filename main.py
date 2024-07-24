#!/usr/bin/env python3

import itertools
import pygame
import sys
from pprint import pprint

from pathlib import Path
from typing import Dict

from src.engine import *
from src.player import *


clock = pygame.time.Clock()

tiles = [
    imgload("resources", "images", "tile_g.png"),
    imgload("resources", "images", "tile.png"),
]


class World:
    def __init__(self):
        keys = [x + (0,) for x in itertools.product(range(20), range(20))]
        left_wall = [(0, y, z) for y in range(10) for z in range(10)]
        right_wall = [(x, 0, z) for x in range(10) for z in range(10)]
        map_ = keys + left_wall + right_wall
        self.data = dict.fromkeys(map_, None)
        self.data = {k: 0 for k in self.data}
        self.data[(2, 2, 0)] = 1


world = World()
surfs = [gen_char() for _ in range(20)]


def main():
    buttons: Dict[str, Button] = {
        "b": ButtonToggle((100, 100), 24, "toggle", 10),
        "title": ButtonLabel(
            (100, 200), 20, "BOTH", lambda: game.set_state(States.PLAY)
        ),
    }

    interactives = [
        Interactive(
            Path("resources", "images", "chest.png"),
            (0, 0),
            Interactive.DIALOGUE,
            dialogues=[Dialogue("Wow this alley really is atomic!", "Dexter")],
        )
    ]

    # tw = TextWriter("Atomic Alley", (300, 300), FontSize.DIALOGUE, Colors.WHITE)
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
                        elif game.state == States.MENU:
                            game.set_state(States.PLAY)

                    elif event.key == pygame.K_SPACE:
                        player.dash()

        display.fill(Colors.GRAYS[50])

        player.scroll()

        for pos, tile in world.data.items():
            x, y, z = pos
            # minimap
            mm_x = x * MMS
            mm_y = y * MMS
            # pygame.draw.rect(display, [255 - z / 10 * 255] * 3, (mm_x, mm_y, MMS, MMS))
            # pygame.draw.rect(display, Colors.BLACK, (mm_x, mm_y, MMS, MMS), 1)
            if tile or True:
                blit_x, blit_y = cart_to_iso(x, y, z)
                # map
                blit_x -= game.scroll[0]
                blit_y -= game.scroll[1]
                # pygame.draw.aacircle(display, Colors.RED, (blit_x, blit_y), 5)
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

        pygame.display.update()
        clock.tick(game.target_fps)


if __name__ == "__main__":
    main()
