from .engine import *


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.image = pygame.transform.scale_by(pygame.image.load("./assets/diag_player.png"), R)
        self.width, self.height = self.image.get_size()

    def update(self):
        self.keys()
        self.draw()
    
    def keys(self):
        keys = pygame.key.get_pressed()
        left = right = top = bottom = False
        m = 0.2
        if keys[pygame.K_a]:
            left = True
        if keys[pygame.K_d]:
            right = True
        if keys[pygame.K_w]:
            top = True
        if keys[pygame.K_s]:
            bottom = True
        if top:
            if left:
                self.x -= m
            elif right:
                self.y -= m
            else:
                self.x -= m * sqrt(0.5)
                self.y -= m * sqrt(0.5)
        elif bottom:
            if left:
                self.y += m
            elif right:
                self.x += m
            else:
                self.x += m * sqrt(0.5)
                self.y += m * sqrt(0.5)
        elif left:
            self.x -= m * sqrt(0.5)
            self.y += m * sqrt(0.5)
        elif right:
            self.x += m * sqrt(0.5)
            self.y -= m * sqrt(0.5)

    def draw(self):
        blit_x, blit_y = cart_to_iso(self.x, self.y, 1)
        display.blit(self.image, (blit_x, blit_y))