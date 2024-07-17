#!/usr/bin/env python3

import pygame
import sys
from src.engine import *


def main():
    b = ButtonToggle((100, 100), (24, 24), "toggle", 10)
    title = ButtonLabel((200, 200), 20, "BOTH", lambda: game.set_state(States.PLAY))

    while game.running:
        for event in pygame.event.get():
            b.process_event(event)
            title.process_event(event)

            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        display.fill((0, 0, 0))

        b.update()
        title.update()

        pygame.display.update()
        clock.tick(game.target_fps)


if __name__ == "__main__":
    main()
