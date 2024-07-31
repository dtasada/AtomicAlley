#!/usr/bin/env python3

import pygame
import sys
import asyncio
from contextlib import suppress

from threading import Thread

from src.artifacts import *
from src.buttons import *
from src.engine import *
from src.objects import *
from src.player import *
from src.workbench import *
from src.enemies import *
from src.writers import *


clock = pygame.time.Clock()
tiles = imgload("resources", "images", "tiles", "tile_sheet.png", columns=6)
# tiles.extend(
#     [
#         imgload("resources", "images", "tiles", "bar.png"),
#         imgload("resources", "images", "tiles", "burger.png"),
#     ]
# )
tiles.extend([
    imgload("resources", "images", "tiles", "workbench.png")
])

head = Node([0, 0, 200, 200])
head.split(-1)
head.draw_paths()

ground = 5
wall = 1
bridge = 3
bar1, bar2 = 0, 4
# bar = 6
invisible = "i"
red = 2
brew = 6


def generate_world():
    en = False
    game.loading = True
    game.loading_progress = 0
    world.data = []
    for leaf in head.get_leaves():
        for xo in range(leaf.room[2]):
            for yo in range(leaf.room[3]):
                x, y = leaf.room[0] + xo, leaf.room[1] + yo
                if leaf.room_type == RoomType.BAR:
                    ground_tile = ((xo + yo) % 2 == 0) * 4
                elif leaf.room_type == RoomType.NORMAL:
                    ground_tile = ground
                    if leaf.has_chest and (xo, yo) == leaf.chest_offset:
                        # chest on the ground
                        interactive = Interactive(
                            "Workbench",
                            imgload("resources", "images", "tiles", "workbench.png"),
                            (leaf.room[0] + leaf.chest_offset[0], leaf.room[1] + leaf.chest_offset[1]),
                            other_lambda=lambda x: workbench_ui.enable(),
                        )
                        world.interactives[(x, y)] = interactive
                world.data.append(
                    ((x, y, 0), ground_tile)
                )
                # chance to drop flask
                if rand(1, 300) == 1:
                    interactive = Artifacts.ERLENMEYER_FLASK.to_world((x, y))
                    interactive.other_lambda = player.new_inventory_item
                    world.interactives[(x, y)] = interactive
                if rand(1, 300) == 1 and not en:
                    enemy = Enemy(x, y)
                    print(x, y)
                    world.enemies[(x, y)] = enemy
                    en = True
                # walls
                if xo in (0, leaf.room[2] - 1) or yo in (0, leaf.room[3] - 1):
                    for zo in range(game.wall_height):
                        zo += 1
                        world.data.append(((leaf.room[0] + xo, leaf.room[1] + yo, zo), wall))

    # for start, end in corridors:
    #     if start[0] == end[0]:
    #         # xs are equal, so vertical bar, so vary horizontally
    #         y = start[1]
    #         while y != end[1]:
    #             y += sign(end[1] - start[1])
    #             for o in range(-2, 3):
    #                 # remove walls for entrance
    #                 if ((start[0] + o, y, 1), wall) in world.data:
    #                     for zo in range(game.wall_height):
    #                         zo += 1
    #                         world.data.remove(((start[0] + o, y, zo), wall))
    #                 # invisible walls
    #                 pass
    #                 # make bridge
    #                 world.try_modifying(((start[0] + o, y, 0), bridge))
    #     elif start[1] == end[1]:
    #         # ys are equal, so horizontal bar, so vary vertically
    #         x = start[0]
    #         while x != end[0]:
    #             x += sign(end[0] - start[0])
    #             for o in range(-2, 3):
    #                 # remove walls for entrance
    #                 if ((x, start[1] + o, 1), wall) in world.data:
    #                     for zo in range(game.wall_height):
    #                         zo += 1
    #                         world.data.remove(((x, start[1] + o, zo), wall))
    #                 # invisible walls
    #                 pass
    #                 # make bridge
    #                 world.try_modifying(((x, start[1] + o, 0), bridge))

    #     game.loading_progress += 1 / len(corridors)
    #     game.progress_bar_image = game.progress_bar_images[
    #         min(floor(len(game.progress_bar_images) * game.loading_progress), 10)
    #     ]  # using min bc sometimes index gets to 11? lol skil isue

    # sort the list (use z-buffering)
    world.data.sort(key=lambda x: (x[0][2], x[0][0], x[0][1]))

    # convert tuples to a dictionary
    world.data = {k: v for k, v in world.data}

    # stop loading sign
    game.loading = False
    game.set_state(States.PLAY)

    game.loading_progress = 0


async def main(debug=False):
    buttons = {
        States.MAIN_MENU: [
            ButtonToggle((100, 100), 40, "toggle", 10),
            ButtonLabel((100, 200), 20, "BOTH", lambda: game.set_state(States.PLAY)),
        ],
        States.MAIN_MENU: [
            ButtonLabel(
                (display.get_width() / 2, display.get_height() / 2),
                100,
                "PLAY",
                lambda: game.set_state(States.PLAY),
            ),
        ],
    }

    title_images = [
        imgload("resources", "images", "menu", "title0.png", scale=5),
        imgload("resources", "images", "menu", "title1.png", scale=5),
    ]
    last_started = ticks()
    buzzing = True
    show_any_key = True

    game.set_state(States.MAIN_MENU)

    if not debug or True:
        game.dialogue = Dialogue("Press <i> to show hotbar & inventory\nPress <o> to show abilities", "Game")

    while game.running:
        game.late_events = []
        for event in pygame.event.get():
            game.late_events.append(event)
            for state, array in buttons.items():
                for button in array:
                    if state == game.state:
                        button.process_event(event)
            
            if workbench_ui.enabled:
                for row in workbench_ui.items:
                    for item in row:
                        if item is not None:
                            item.process_event(event)

            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                case pygame.KEYDOWN:
                    if game.state == States.MAIN_MENU:
                        if event.key == pygame.K_z:
                            show_any_key = False
                            Thread(target=generate_world, daemon=True).start()

                    if event.key == pygame.K_ESCAPE:
                        match game.state:
                            case States.PLAY:
                                if workbench_ui.enabled:
                                    workbench_ui.disable()
                                else:
                                    game.set_state(States.MAIN_MENU)
                            case States.MAIN_MENU:
                                game.set_state(States.PLAY)
                    
                    elif event.key == pygame.K_f:
                        world.data[(10, 10, 1)] = 2
                
            if game.state == States.PLAY:
                player.process_event(workbench_ui, event)

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

                text_pos = (display.get_width() / 2, 6 * display.get_height() / 7)
                if show_any_key:
                    write(
                        display,
                        "center",
                        "press <z> to continue",
                        fonts[25],
                        Colors.WHITE,
                        *text_pos,
                    )

                if game.loading:
                    display.blit(
                        game.progress_bar_image,
                        (
                            text_pos[0] - game.progress_bar_image.get_width() / 2,
                            text_pos[1] - game.progress_bar_image.get_height() / 2,
                        ),
                    )

            case States.PLAY:
                display.fill(Colors.GRAYS[30])

                player.check_rects = []
                world.late_interactives = []
                world.late_enemies = []
                world.already_interacted = False
                for xo in range(-20, 21):
                    for yo in range(-20, 21):
                        # UPDATE TILES
                        for zo in range(6):
                            x, y, z = int(player.x) + xo, int(player.y) + yo, zo
                            if (x, y, z) not in world.data:
                                continue
                            tile = world.data[(x, y, z)]
                            if z > 0:
                                rect = pygame.Rect(x * game.rect_scale, y * game.rect_scale, 20, 20)
                                player.check_rects.append(rect)
                            # pygame.draw.rect(display, [255 - z / 10 * 255] * 3, (mm_x, mm_y, MMS, MMS))
                            # pygame.draw.rect(display, Colors.BLACK, (mm_x, mm_y, MMS, MMS), 1)
                            if tile != "i":
                                blit_x, blit_y = cart_to_iso(x, y, z)
                                # map
                                blit_x -= game.scroll[0]
                                blit_y -= game.scroll[1]
                                display.blit(tiles[tile], (blit_x, blit_y))
                        # UPDATE INTERACTIVES
                        x, y = int(player.x) + xo, int(player.y) + yo
                        if (x, y) in world.interactives:
                            interactive = world.interactives[(x, y)]
                            world.late_interactives.append(interactive)
                         
                        # update enemies
                        if (x, y) in world.enemies:
                            enemy = world.enemies[(x, y)]
                            world.late_enemies.append(enemy)

                for interactive in world.late_interactives:
                    x, y = interactive.wpos
                    if not world.already_interacted and abs(x - player.x) <= 2 and abs(y - player.y) <= 2:
                        interactive.focused = True
                        world.already_interacted = True
                    else:
                        interactive.focused = False
                    interactive.update()
                    for event in game.late_events:
                        interactive.process_event(event)
                
                for enemy in world.late_enemies:
                    enemy.update(player)
                    print(enemy.last_x, enemy.last_y)
                    # take damage
                    if player.slashing:
                        if player.slash_rect.colliderect(enemy.srect):
                            if not enemy.taking_damage:
                                if enemy.hp - player.slash_damage > 0:
                                    enemy.take_damage(player.slash_damage, player.it)
                                    all_particles.append(DamageIndicator(10, True, enemy))
                                else:
                                    enemy.kill()
                                    all_particles.append(DamageIndicator("KO!", True, enemy))
                        break
                for shadow in all_shadows:
                    shadow.update()

                # for leaf in head.get_leaves():
                #     pygame.draw.rect(display, leaf.color, leaf.border)
                #     pygame.draw.rect(display, Colors.BLACK, leaf.room)
                # head.draw_paths()

                # for cr in player.check_rects:
                #     pygame.draw.rect(display, [220, 220, 220], cr)

                player.update()
                player.scroll()
                workbench_ui.update()
                player.render_hotbar()

         

                for particle in all_particles:
                    particle.update()
                
                write(display, "center", (int(player.x), int(player.y)), fonts[30], Colors.WHITE, player.srect.centerx, player.srect.top - 50)

                write(
                    display,
                    "topright",
                    int(clock.get_fps()),
                    fonts[25],
                    Colors.WHITE,
                    display.get_width() - 9,
                    5,
                )

                display.blit(player.black_surf, (0, 0))
                if player.black_surf.get_alpha() >= 65:
                    for x, ability in enumerate(player.abilities):
                        rect = pygame.Rect((0, 0, 43 * R, 43 * R))
                        rect.center = (display.get_width() / 2, display.get_height() / 2)
                        rect.x += x * 50 * R - 80
                        display.blit(ability.image, rect)
                        text_x, text_y = pygame.mouse.get_pos()
                        text_y += 80
                        if rect.collidepoint(pygame.mouse.get_pos()):
                            text = ability.text
                            if ability.type_ == PlayerAbilityTypes.SLASH:
                                text += f"\nCurrent damage: {player.slash_damage}"
                            elif ability.type_ == PlayerAbilityTypes.DASH:
                                text += f"\nCurrent damage: {player.dash_damage}"
                            write(display, "midtop", text, fonts[30], Colors.WHITE, text_x, text_y)

                for state, array in buttons.items():
                    for button in array:
                        if state == game.state:
                            button.update()

                if game.dialogue is not None:
                    for event in game.late_events:
                        if game.dialogue is not None:
                            game.dialogue.process_event(event)
                    if game.dialogue is not None:
                        game.dialogue.update()

        if game.screen_shake_mult > 0:
            game.screen_shake_offset = [
                randf(-game.screen_shake_mult, game.screen_shake_mult),
                randf(-game.screen_shake_mult, game.screen_shake_mult),
            ]
            if ticks() - game.last_screen_shake >= game.screen_shake_duration:
                game.screen_shake_offset = [0, 0]
                game.screen_shake_mult = 0
        window.blit(display, game.screen_shake_offset)

        pygame.display.update()

        clock.tick(game.target_fps)

        await asyncio.sleep(0)

asyncio.run(main())
