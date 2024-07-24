#!/usr/bin/env python3

from operator import lt
import pygame
import sys

from pathlib import Path
from typing import Dict

from src.buttons import *
from src.engine import *
from src.objects import *
from src.player import *
from src.writers import *

player = Player()
world = World()
# workbench_ui = WorkBenchUI()
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
            "Chest",
            Path("resources", "images", "chest.png"),
            (0, 0),
            Interactive.DIALOGUE,
            dialogues=[Dialogue("Wow this alley really is atomic!", "Dexter")],
        ),
        Interactive(
            "Workbench",
            Path("resources", "images", "workbench.png"),
            (2, 2),
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
                    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                        if game.state == States.PLAY:
                            game.set_state(States.MENU)
                        elif game.state == States.MENU:
                            game.set_state(States.PLAY)

        display.fill(Colors.GRAYS[50])

        player.scroll()

        display.fill(Colors.LIGHT_GRAY)

        for pos, tile in world.data.items():
            x, y = pos
            # minimap
            mm_x = x * MMS
            mm_y = y * MMS
            pygame.draw.rect(display, (106, 190, 48), (mm_x, mm_y, MMS, MMS))
            pygame.draw.rect(display, WHITE, (mm_x, mm_y, MMS, MMS), 1)
            if tile > 0:
                blit_x, blit_y = cart_to_iso(x, y, 0)
                # display.blit(pygame.font.SysFont("Times New Roman", 14).render(f"{x},{y}", True, BLACK), (blit_x, blit_y))
                # map
                blit_x -= game.scroll[0]
                blit_y -= game.scroll[1]
                display.blit(tiles[tile], (blit_x, blit_y))

        for i in interactives:
            i.update(player, interactives)

        player.update()
        if game.state == States.MENU:
            for button in buttons.values():
                button.update()

        if game.dialogue:
            game.dialogue.update()

        pygame.display.update()
        clock.tick(game.target_fps)


if __name__ == "__main__":
    main()
