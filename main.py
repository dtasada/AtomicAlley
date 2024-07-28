#!/usr/bin/env python3

import pygame
import sys

from threading import Thread

from src.artifacts import *
from src.buttons import *
from src.engine import *
from src.objects import *
from src.player import *
from src.workbench import *
from src.writers import *

clock = pygame.time.Clock()
tiles = imgload("resources", "images", "tiles", "tile_sheet.png", columns=4)
tiles.extend(
    [
        imgload("resources", "images", "tiles", "bar.png"),
        imgload("resources", "images", "tiles", "burger.png"),
    ]
)

pbi = pygame.image.load(Path("resources", "images", "menu", "loading.png"))

head = Node([0, 0, 200, 200])
head.split(-1)
head.draw_paths()


def generate_world():
    game.loading = True
    game.loading_progress = 0
    world.data = []
    for leaf in head.get_leaves():
        for xo in range(leaf.room[2]):
            for yo in range(leaf.room[3]):
                world.data.append(
                    ((leaf.room[0] + xo, leaf.room[1] + yo, 0), World.Colors.RGB)
                )
                if xo in (0, leaf.room[2] - 1) or yo in (0, leaf.room[3] - 1):
                    for zo in range(1, 5):
                        world.data.append(
                            (
                                (leaf.room[0] + xo, leaf.room[1] + yo, zo),
                                World.Colors.WHITE,
                            )
                        )

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

        game.loading_progress += 1 / len(corridors)

        game.progress_bar_image = game.progress_bar_images[
            floor(len(game.progress_bar_images) * game.loading_progress)
        ]

    # sort the list (use z-buffering)
    world.data.sort(key=lambda x: x[0])

    # convert tuples to a dictionary
    world.data = {k: v for k, v in world.data}

    # stop loading sign
    game.loading = False
    game.set_state(States.PLAY)


def main():
    buttons = {
        States.MAIN_MENU: [
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
            imgload("resources", "images", "tiles", "chest.png"),
            (1, 1),
            Interactive.DIALOGUE,
            dialogues=[Dialogue("Wow this alley really is atomic!", "Dexter")],
        ),
        Interactive(
            "Workbench",
            imgload("resources", "images", "tiles", "workbench.png"),
            (4, 2),
            other_lambda=lambda: workbench_ui.enable(),
        ),
        Artifacts.TONIC_OF_LIFE.to_world((6, 6)),
    ]

    title_images = [
        imgload("resources", "images", "menu", "title0.png", scale=5),
        imgload("resources", "images", "menu", "title1.png", scale=5),
    ]
    last_started = ticks()
    buzzing = True
    show_any_key = True

    game.set_state(States.MAIN_MENU)
    while game.running:
        for event in pygame.event.get():
            for state, array in buttons.items():
                for button in array:
                    if state == game.state:
                        button.process_event(event)

            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                case pygame.KEYDOWN:
                    if game.state == States.MAIN_MENU:
                        if event.key == pygame.K_z:
                            show_any_key = False
                            Thread(target=generate_world, daemon=True).start()

                    elif game.state == States.PLAY:
                        player.handle_keypress(event)

                    if event.key == pygame.K_ESCAPE:
                        match game.state:
                            case States.PLAY:
                                if workbench_ui.enabled:
                                    workbench_ui.disable()
                                else:
                                    game.set_state(States.MAIN_MENU)
                            case States.MAIN_MENU:
                                game.set_state(States.PLAY)

        match game.state:
            case States.MAIN_MENU:
                if random.randint(0, 100) > 94:
                    title = title_images[1]
                    if buzzing:
                        buzzing = False
                        buzzing_channel.pause()
                else:
                    title = title_images[0]
                    if not buzzing:
                        buzzing_channel.unpause()
                display.blit(title, (0, 0))

                if ticks() - last_started >= 500:
                    if not game.loading:
                        show_any_key = not show_any_key
                        last_started = ticks()

                text_pos = (display.width / 2, 6 * display.height / 7)
                if show_any_key:
                    write(
                        display,
                        "center",
                        "press [z] to continue",
                        fonts[25],
                        Colors.WHITE,
                        *text_pos,
                    )

                if game.loading:
                    display.blit(
                        game.progress_bar_image,
                        (
                            text_pos[0] - game.progress_bar_image.width / 2,
                            text_pos[1] - game.progress_bar_image.height / 2,
                        ),
                    )

            case States.PLAY:
                display.fill(Colors.GRAYS[30])

                for xo in range(-20, 21):
                    for yo in range(-20, 21):
                        for zo in range(6):
                            x, y, z = int(player.x) + xo, int(player.y) + yo, zo
                            if (x, y, z) not in world.data:
                                continue
                            tile = world.data[(x, y, z)]

                            # minimap
                            if tile or True:
                                blit_x, blit_y = cart_to_iso(x, y, z)
                                # map
                                blit_x -= game.scroll[0]
                                blit_y -= game.scroll[1]
                                display.blit(tiles[tile], (blit_x, blit_y))

                for interactive in interactives:
                    interactive.update(player, interactives)

                for shadow in all_shadows:
                    shadow.update()

                for leaf in head.get_leaves():
                    pygame.draw.rect(display, leaf.color, leaf.border)
                    pygame.draw.rect(display, Colors.BLACK, leaf.room)
                head.draw_paths()

                player.update()
                player.scroll()

                for particle in all_particles:
                    particle.update()

                write(
                    display,
                    "topright",
                    int(clock.get_fps()),
                    fonts[25],
                    Colors.WHITE,
                    display.width - 9,
                    5,
                )
                write(
                    display,
                    "center",
                    f"{player.x:.0f},{player.y:.0f}",
                    fonts[30],
                    Colors.WHITE,
                    player.srect.centerx,
                    player.srect.top - 30,
                )

                write(
                    display,
                    "topleft",
                    "press [i] to show inventory",
                    fonts[20],
                    Colors.WHITE,
                    5,
                    5,
                )
                write(
                    display,
                    "topleft",
                    "press [o] to show abilities",
                    fonts[20],
                    Colors.WHITE,
                    5,
                    35,
                )

                display.blit(player.black_surf, (0, 0))

                for state, array in buttons.items():
                    for button in array:
                        if state == game.state:
                            button.update()

                if game.dialogue:
                    game.dialogue.update()

                workbench_ui.update()

        pygame.display.update()


if __name__ == "__main__":
    main()
