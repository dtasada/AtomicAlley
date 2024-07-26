#!/usr/bin/env python3

import pygame
import sys

from pathlib import Path
from typing import Dict

from src.buttons import *
from src.engine import *
from src.objects import *
from src.player import *
from src.writers import *


clock = pygame.time.Clock()
tiles = imgload("resources", "images", "tile_sheet.png", columns=2, frames=2)
tiles.extend([
    imgload("resources", "images", "tile_0.png"),
    imgload("resources", "images", "tile_1.png"),
])

# 0 = black
# 1 = white
# 2 = gray
# 3 = rgb

# workbench_ui = WorkBenchUI()
surfs = [gen_char() for _ in range(20)]

head = Node([0, 0, 200, 200])
head.split(-1)
head.draw_paths()

poss = []
for leaf in head.get_leaves():
    for xo in range(leaf.room[2]):
        for yo in range(leaf.room[3]):
            poss.append((leaf.room[0] + xo, leaf.room[1] + yo, 0, 2))
            # if xo in (0, leaf.room[2] - 1) or yo in (0, leaf.room[3] - 1):
            #     poss.append((leaf.room[0] + xo, leaf.room[1] + yo, 1, 3))
world.data = {data[:3]: data[3] for data in poss}
for start, end in corridors:
    if start[0] == end[0]:
        y = start[1]
        while y != end[1]:
            y += sign(end[1] - start[1])
            world.data[(start[0], y, 0)] = 2
    elif start[1] == end[1]:
        x = start[0]
        while x != end[0]:
            x += sign(end[0] - start[0])
            world.data[(x, start[1], 0)] = 2


def main():
    buttons: Dict[str, Button] = {
        "b": ButtonToggle((100, 100), 24, "toggle", 10),
        "title": ButtonLabel(
            (100, 200), 20, "BOTH", lambda: game.set_state(States.PLAY)
        ),
    }

    interactives = [
        Interactive(
            "Chest",
            Path("resources", "images", "chest.png"),
            (1, 1),
            Interactive.DIALOGUE,
            dialogues=[Dialogue("Wow this alley really is atomic!", "Dexter")],
        ),
        Interactive(
            "Workbench",
            Path("resources", "images", "workbench.png"),
            (4, 2),
            Interactive.MUT_STATE,
            target_state=States.WORKBENCH,
        ),
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

        display.fill(Colors.GRAYS[30])

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
        
        write(display, "center", f"{player.x:.0f},{player.y:.0f}", fonts[30], Colors.WHITE, player.srect.centerx, player.srect.top - 30)
        for interactive in interactives:
            if player.rect.bottom < interactive.rect.bottom:
                interactive.update(player, interactives)

        player.update()

        for interactive in interactives:
            if player.rect.bottom > interactive.rect.bottom:
                interactive.update(player, interactives)

        if game.state == States.MENU:
            for button in buttons.values():
                button.update()

        write(
           display,  "topright", int(clock.get_fps()), fonts[25], Colors.GRAYS[200], WIDTH - 9, 5
        )
        if game.state == States.MENU:
            for button in buttons.values():
                button.update()

        if game.dialogue:
            game.dialogue.update()

        pygame.display.update()
        dt = clock.tick(game.target_fps) / (1 / game.target_fps)


if __name__ == "__main__":
    main()
