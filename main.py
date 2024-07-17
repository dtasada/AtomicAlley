#!/usr/bin/env python3

import pygame
from sys import exit
from src.engine import *

pygame.init()


# test_font = pygame.font.Font("path/font.ttf")


def main():
    clock = pygame.time.Clock()
    display = pygame.display.set_mode((1280, 720))

    game = Game()

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.update()
        clock.tick(game.target_fps)
