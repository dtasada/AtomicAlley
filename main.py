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
tiles = imgload("resources", "images", "tiles", "tile_sheet.png", columns=4, frames=4)
tiles.extend([
    imgload("resources", "images", "tiles", "bar.png"),
    imgload("resources", "images", "tiles", "burger.png"),
])

# workbench_ui = WorkBenchUI()
head = Node([0, 0, 200, 200])
head.split(-1)
head.draw_paths()

# poss = []
world.data = []
for leaf in head.get_leaves():
    for xo in range(leaf.room[2]):
        for yo in range(leaf.room[3]):
            world.data.append(((leaf.room[0] + xo, leaf.room[1] + yo, 0), 3))
            if xo in (0, leaf.room[2] - 1) or yo in (0, leaf.room[3] - 1):
                for zo in range(1, 5):
                    world.data.append(((leaf.room[0] + xo, leaf.room[1] + yo, zo), 1))
# world.data = [(data[:3], data[3]) for data in poss]
for start, end in corridors:
    if start[0] == end[0]:
        # xs are equal, so vertical bar, so vary horizontally
        y = start[1]
        while y != end[1]:
            y += sign(end[1] - start[1])
            for o in range(-2, 3):
                world.try_modifying(((start[0] + o, y, 0), 1))
    elif start[1] == end[1]:
        # ys are equal, so horizontal bar, so vary vertically
        x = start[0]
        while x != end[0]:
            x += sign(end[0] - start[0])
            for o in range(-2, 3):
                world.try_modifying(((x, start[1] + o, 0), 1))
# sort the list (use z-buffering)
world.data.sort(key=lambda x: x[0])
# convert tuples to a dictionary
world.data = {k: v for k, v in world.data}

bg = imgload("resources", "images", "bg.png")

surf = pygame.Surface((40, 40), pygame.SRCALPHA)
surf.fill(Colors.WHITE)
write(surf, "center", "Bi", fonts[24], Colors.BLACK, *[s / 2 for s in surf.size])



def main():
    bg_y = 0
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

    # interactives = [
    #     Interactive(
    #         "Chest",
    #         Path("resources", "images", "tiles", "chest.png"),
    #         (1, 1),
    #         Interactive.DIALOGUE,
    #         dialogues=[Dialogue("Wow this alley really is atomic!", "Dexter")],
    #     ),
    #     Interactive(
    #         "Workbench",
    #         Path("resources", "images", "tiles", "workbench.png"),
    #         (4, 2),
    #         Interactive.MUT_STATE,
    #         target_state=States.WORKBENCH,
    #         other_lambda=lambda: workbench_ui.gen_grid(),
    #     ),
    #     Artifacts.TONIC_OF_LIFE().to_world((6, 6)),
    # ]
    interactives = []

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

        display.fill(Colors.GRAYS[30])
        display.blit(bg, (0, bg_y))
        display.blit(bg, (0, bg_y - bg.height))
        bg_y += 1
        if bg_y >= display.height:
            bg_y = 0

        player.scroll()

        num = 0
        for xo in range(-20, 21):
            for yo in range(-20, 21):
                for zo in range(20):
                    x, y, z = int(player.x) + xo, int(player.y) + yo, zo
                    if (x, y, z) in world.data:
                        tile = world.data[(x, y, z)]
                        # minimap
                        # mm_x = x * MMS
                        # mm_y = y * MMS
                        # pygame.draw.rect(display, [255 - z / 10 * 255] * 3, (mm_x, mm_y, MMS, MMS))
                        # pygame.draw.rect(display, Colors.BLACK, (mm_x, mm_y, MMS, MMS), 1)
                        blit_x, blit_y = cart_to_iso(x, y, z)
                        # map
                        blit_x -= game.scroll[0]
                        blit_y -= game.scroll[1]
                        display.blit(tiles[tile], (blit_x, blit_y))
                        num += 1
        write(display, "topright", num, fonts[25], Colors.WHITE, display.width - 8, 30)

        for shadow in all_shadows:
            shadow.update()

        for leaf in head.get_leaves():
            pygame.draw.rect(display, leaf.color, leaf.border)
            pygame.draw.rect(display, Colors.BLACK, leaf.room)

        head.draw_paths()
        player.update()

        for particle in all_particles:
            particle.update()

        write(display, "topright", int(clock.get_fps()), fonts[25], Colors.WHITE, display.width - 9, 5)
        
        # write(display, "center", f"{player.x:.0f},{player.y:.0f}", fonts[30], Colors.WHITE, player.srect.centerx, player.srect.top - 30)
        for interactive in interactives:
            if player.rect.bottom < interactive.rect.bottom:
                interactive.update(player, interactives)


        # for interactive in interactives:
        #     if player.rect.bottom > interactive.rect.bottom:
        #         interactive.update(player, interactives)

        # if game.state == States.MENU:
        #     for button in buttons.values():
        #         button.update()

        write(
            display,
            "topright",
            int(clock.get_fps()),
            fonts[25],
            Colors.WHITE,
            display.width - 9,
            5,
        )
        # for interactive in interactives:
        #     interactive.update(player, interactives)

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
        
        display.blit(surf, pygame.mouse.get_pos())

        pygame.display.update()
        dt = clock.tick(game.target_fps) / (1 / game.target_fps)


if __name__ == "__main__":
    main()
