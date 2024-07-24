from .engine import *

from math import sqrt


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.blit_x = self.blit_y = 0 
        self.images = {
            ("bottomleft", "bottom", "right", "topright", "top")[i]: 
            imgload(
            "resources", "images", "player_sheet.png", columns=7, row=i, rows=5, frames=1
            )
            for i in range(5)
        }
        self.images["left"] = [pygame.transform.flip(i, True, False) for i in self.images["right"]]
        self.images["bottomright"] = [pygame.transform.flip(i, True, False) for i in self.images["bottomleft"]]
        self.images["topleft"] = [pygame.transform.flip(i, True, False) for i in self.images["topright"]]
        
        self.run_frames = {
            ("bottomleft", "bottom", "right", "topright", "top")[i]:
            imgload(
            "resources", "images", "player_sheet.png", columns=7, row=i, rows=5, start_frame=1, frames=6
            ) 
            for i in range(5)
        }
        self.run_frames["left"] = [pygame.transform.flip(i, True, False) for i in self.run_frames["right"]]
        self.run_frames["bottomright"] = [pygame.transform.flip(i, True, False) for i in self.run_frames["bottomleft"]]
        self.run_frames["topleft"] = [pygame.transform.flip(i, True, False) for i in self.run_frames["topright"]]

        self.current_frame = 0
        self.it = "bottom"
        self.image = self.images[self.it][self.current_frame]
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.srect = self.image.get_rect()
        self.yvel = 0
        self.animate_run = False

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
            self.animate_run = True
            left = True
        if keys[pygame.K_d]:
            self.animate_run = True
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

        if self.animate_run:
            if self.current_frame > len(self.run_frames[self.it])-1:
                self.current_frame = 0
            self.image = self.run_frames[self.it][int(self.current_frame)]
            self.current_frame += 0.15
            self.animate_run = False
        else:
            self.current_frame = 0
            self.image = self.images[self.it][int(self.current_frame)]

        display.blit(self.image, self.srect)
