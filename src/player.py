from .engine import *


class Player:
    def __init__(self):
        self.x = 5
        self.y = 4
        self.image = pygame.transform.scale_by(
            pygame.image.load("resources/images/diag_player.png"), 2
        )

    @property
    def mm_rect(self):
        return (self.x * MMS, self.y * MMS)

    def update(self):
        self.keys()
        self.draw()

    def keys(self):
        keys = pygame.key.get_pressed()
        m = 0.1
        if keys[pygame.K_a]:
            self.x -= 1
        if keys[pygame.K_d]:
            self.x += 1
        if keys[pygame.K_w]:
            self.y -= 1
        if keys[pygame.K_s]:
            self.y += 1

    def draw(self):
        display.draw(self.image, self.mm_rect)

