from .engine import *


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.blit_x = self.blit_y = 0
        self.image = pygame.transform.scale_by(pygame.image.load("./assets/player.png"), R)
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.srect = self.image.get_rect()
        self.yvel = 0

    def update(self):
        self.keys()
        self.draw()
    
    def scroll(self):
        game.fake_scroll[0] += (self.blit_x - game.fake_scroll[0] - WIDTH // 2) * 0.1
        game.fake_scroll[1] += (self.blit_y - game.fake_scroll[1] - HEIGHT // 2) * 0.1
        game.scroll[0] = int(game.fake_scroll[0])
        game.scroll[1] = int(game.fake_scroll[1])

    def keys(self):
        keys = pygame.key.get_pressed()
        left = right = top = bottom = False
        m = 0.05
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
        self.blit_x, self.blit_y = cart_to_iso(self.x, self.y, 0)
        self.blit_x += S / 2
        self.blit_y += S / 4
        #
        self.blit_y += 8
        self.rect.midbottom = (self.blit_x, self.blit_y)
        self.srect.midbottom = (self.blit_x, self.blit_y)
        self.srect.x -= game.scroll[0]
        self.srect.y -= game.scroll[1]
        display.blit(self.image, self.srect)