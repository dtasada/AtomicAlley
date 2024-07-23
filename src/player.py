from .engine import *
from pathlib import Path


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.blit_x = self.blit_y = 0
        self.image_sprs = imgload("resources", "images", "player_sheet.png", frames=5, vertical=True)
        self.images = {("bottomleft", "bottom", "right", "topright", "top")[i]: self.image_sprs[i] for i in range(5)}
        self.images["left"] = pygame.transform.flip(self.images["right"], True, False)
        self.images["bottomright"] = pygame.transform.flip(self.images["bottomleft"], True, False)
        self.images["topleft"] = pygame.transform.flip(self.images["topright"], True, False)
        self.it = "bottom"
        self.image = self.images[self.it]
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.srect = self.image.get_rect()
        self.yvel = 0

    def update(self):
        self.keys()
        self.draw()
    
    def scroll(self):
        game.fake_scroll[0] += (self.rect.centerx - game.fake_scroll[0] - WIDTH // 2) * 0.1
        game.fake_scroll[1] += (self.rect.centery - game.fake_scroll[1] - HEIGHT // 2) * 0.1
        game.scroll[0] = int(game.fake_scroll[0])
        game.scroll[1] = int(game.fake_scroll[1])

    def keys(self):
        keys = pygame.key.get_pressed()
        left = right = top = bottom = False
        m = 0.05
        mods = pygame.key.get_mods()
        if mods == 1:
            m *= 2
        if keys[pygame.K_a]:
            left = True
        if keys[pygame.K_d]:
            right = True
        if keys[pygame.K_w]:
            top = True
        if keys[pygame.K_s]:
            bottom = True
        # self.it = image type, e.g. topleft, bottom, etc.
        if top:
            if left:
                self.x -= m
                self.it = "topleft"
            elif right:
                self.y -= m
                self.it = "topright"
            else:
                self.x -= m * sqrt(0.5)
                self.y -= m * sqrt(0.5)
                self.it = "top"
        elif bottom:
            if left:
                self.y += m
                self.it = "bottomleft"
            elif right:
                self.x += m
                self.it = "bottomright"
            else:
                self.x += m * sqrt(0.5)
                self.y += m * sqrt(0.5)
                self.it = "bottom"
        elif left:
            self.x -= m * sqrt(0.5)
            self.y += m * sqrt(0.5)
            self.it = "left"
        elif right:
            self.x += m * sqrt(0.5)
            self.y -= m * sqrt(0.5)
            self.it = "right"

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
        self.image = self.images[self.it]
        display.blit(self.image, self.srect)
