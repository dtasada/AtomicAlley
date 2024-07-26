#!/usr/bin/env python3

import pygame
import sys

from pathlib import Path

from src.artifacts import *
from src.buttons import *
from src.engine import *
from src.objects import *
from src.player import *
from src.workbench import *
from src.writers import *


clock = pygame.time.Clock()

tiles = [
    imgload("resources", "images", "tiles", "tile_0.png"),
    imgload("resources", "images", "tiles", "tile_1.png"),
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
    buttons = {
        States.MENU: [
            ButtonToggle((100, 100), 40, "toggle", 10),
            ButtonLabel((100, 200), 20, "BOTH", lambda: game.set_state(States.PLAY)),
        ],
        States.MAIN_MENU: [
            ButtonLabel(
                (display.width / 2, display.height / 2),
                100,
                "PLAY",
                lambda: game.set_state(States.PLAY),
            ),
        ],
    }

    interactives = [
        Interactive(
            "Chest",
            Path("resources", "images", "tiles", "chest.png"),
            (1, 1),
            Interactive.DIALOGUE,
            dialogues=[Dialogue("Wow this alley really is atomic!", "Dexter")],
        ),
        Interactive(
            "Workbench",
            Path("resources", "images", "tiles", "workbench.png"),
            (4, 2),
            Interactive.MUT_STATE,
            target_state=States.WORKBENCH,
            other_lambda=lambda: workbench_ui.gen_grid(),
        ),
        Artifacts.TONIC_OF_LIFE().to_world((6, 6)),
    ]

    # tw = TextWriter("Atomic Alley", (300, 300), FontSize.DIALOGUE, Colors.WHITE)
    while game.running:
        for event in pygame.event.get():
            for state, array in buttons.items():
                [button.process_event(event) for button in array if state == game.state]

            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                case pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        match game.state:
                            case States.PLAY:
                                game.set_state(States.MENU)
                            case States.MENU | States.WORKBENCH:
                                game.set_state(States.PLAY)

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

        for leaf in head.get_leaves():
            pygame.draw.rect(display, leaf.color, leaf.border)
            pygame.draw.rect(display, Colors.BLACK, leaf.room)
        head.draw_paths()
        player.update()

        write(
            display,
            "topright",
            int(clock.get_fps()),
            fonts[25],
            Colors.WHITE,
            display.width - 9,
            5,
        )
        for interactive in interactives:
            interactive.update(player, interactives)

        for state, array in buttons.items():
            [button.update() for button in array if state == game.state]

        # or
        # for state, array in buttons.items():
        #     for button in array:
        #         if state == game.state:
        #             button.update()

        match game.state:
            case States.MENU:
                pass
            case States.WORKBENCH:
                workbench_ui.update()

        if game.dialogue:
            game.dialogue.update()

        pygame.display.update()
        dt = clock.tick(game.target_fps) / (1 / game.target_fps)


if __name__ == "__main__":
    main()
