#!/usr/bin/env python3

import pygame
import sys
from pprint import pprint

from pathlib import Path
from typing import Dict

from src.engine import *
from src.player import *


clock = pygame.time.Clock()

tiles = [
    imgload("resources", "images", "tile_0.png"),
    imgload("resources", "images", "tile_1.png"),
]


class World:
    def __init__(self):
        # keys = [x + (0,) for x in itertools.product(range(20), range(20))]
        # left_wall = [(0, y, z) for y in range(20) for z in range(10)]
        # right_wall = [(x, 0, z) for x in range(20) for z in range(10)]
        # map_ = keys + left_wall + right_wall
        map_ = []
        self.data = dict.fromkeys(map_, None)
        self.data = {k: 0 for k in self.data}
        self.light_data = {k: randf(0.6, 1) for k, v in self.data.items()}
        self.data[(2, 2, 0)] = 1


world = World()
surfs = [gen_char() for _ in range(20)]

head = Node([0, 0, 200, 200])
head.split(-1)

poss = []
for leaf in head.get_leaves():
    for xo in range(leaf.room[2]):
        for yo in range(leaf.room[3]):
            poss.append((leaf.room[0] + xo, leaf.room[1] + yo, 0, 0))
            if xo in (0, leaf.room[2] - 1) or yo in (0, leaf.room[3] - 1):
                poss.append((leaf.room[0] + xo, leaf.room[1] + yo, 1, 1))
world.data = {data[:3]: data[3] for data in poss}

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
                display.blit(tiles[tile], (blit_x, blit_y))

        for shadow in all_shadows:
            shadow.update()

        for button in buttons.values():
            button.update()

        for leaf in head.get_leaves():
            pygame.draw.rect(display, leaf.color, leaf.border)
            pygame.draw.rect(display, Colors.BLACK, leaf.room)
        head.draw_paths()
        player.update()


        write(display, "topright", int(clock.get_fps()), fonts[25], Colors.WHITE, WIDTH - 9, 5)
        if game.state == States.MENU:
            for button in buttons.values():
                button.update()

        pygame.display.update()
        dt = clock.tick(game.target_fps) / (1 / game.target_fps)


if __name__ == "__main__":
    main()
