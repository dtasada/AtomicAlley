from .engine import *


class Enemy(Smart):
    def __init__(self, x, y):
        self.image = pygame.Surface((50, 50))
        self.image.fill([rand(0, 255) for _ in range(3)])
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.mmrect = self.rect.copy()
        self.srect = self.rect.copy()
        self.x, self.y = x, y
        self.hp = 100
        self.slide_pos = None
        self.xvel = self.yvel = 0
        self.last_take_damage = ticks()
    
    def take_damage(self, damage, direc):
        self.hp -= damage
        kwargs = {
            x: direc == x
            for x in (
                "top",
                "topright",
                "right",
                "bottomright",
                "bottom",
                "bottomleft",
                "left",
                "topleft",
            )
        }
        self.xvel, self.yvel, _ = cart_dir_to_vel(**kwargs, m=1)
        self.last_take_damage = ticks()

    def update(self):
        self.draw()
    
    def draw(self):
        self.x += self.xvel
        self.y += self.yvel
        self.xvel += -self.xvel * 0.2
        self.yvel += -self.yvel * 0.2
        if self.xvel <= 0.001:
            self.xvel = 0
        if self.yvel <= 0.001:
            self.yvel = 0
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
