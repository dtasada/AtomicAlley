from .engine import *


class Enemy(Smart):
    def __init__(self, x, y):
        self.rect = pygame.FRect(0, 0, 64, 64)
        self.mmrect = self.rect.copy()
        self.srect = self.rect.copy()
        self.x, self.y = x, y
        self.hp = 100
        self.slide_pos = None
        self.xvel = self.yvel = 0
        self.last_take_damage = ticks()
        self.vmult = 1
        self.taking_damage = True
        self.type = "square"
        if self.type == "square":
            self.color = [rand(0, 255) for _ in range(3)]
            self.image = None
        self.last_movement = ticks()
        self.last_x, self.last_y = x, y

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
        self.xvel, self.yvel, _ = cart_dir_to_vel(**kwargs, m=2)
        self.last_take_damage = ticks()
        self.vmult = 1
        self.taking_damage = True

    def update(self, player):
        self.draw(player)
    
    def draw(self, player):
        # movement
        self.vmult += -self.vmult * 0.1
        # x
        if self.type == "square" and ticks() - self.last_movement >= 2000:
            m = 2
            angle = randf(0, 2 * pi)
            self.xvel = cos(angle) * m
            self.yvel = sin(angle) * m
            self.vmult = 1
            self.last_movement = ticks()
        if self.vmult <= 0.00001:
            self.vmult = 0
        self.xvel *= self.vmult
        self.x += self.xvel
        for cr in player.check_rects:
            if self.mmrect.colliderect(cr):
                if self.xvel * self.vmult > 0:
                    self.mmrect.right = cr.left
                else:
                    self.mmrect.left = cr.right
        # y
        self.yvel *= self.vmult
        self.y += self.yvel * self.vmult
        for cr in player.check_rects:
            if self.mmrect.colliderect(cr):
                if self.yvel * self.vmult > 0:
                    self.mmrect.bottom = cr.top
                else:
                    self.mmrect.top = cr.bottom
        # blit
        self.blit_x, self.blit_y = cart_to_iso(self.x, self.y, 0)
        self.blit_x += S / 2
        self.blit_y += S / 4
        #
        self.blit_y += 8
        self.rect.midbottom = (self.blit_x, self.blit_y)
        self.srect.midbottom = (self.blit_x, self.blit_y)
        self.srect.x -= game.scroll[0]
        self.srect.y -= game.scroll[1]
        if self.type == "square":
            xo = sin(ticks() * 0.006) * 12
            yo = cos(ticks() * 0.006) * 12
            rect = pygame.Rect((0, 0, self.srect.width + xo, self.srect.height + yo))
            rect.center = self.srect.center
            pygame.draw.rect(display, self.color, rect)
        else:
            display.blit(self.image, self.srect)
        # health
        if self.hp < 100:
            health_rect = pygame.Rect((0, 0, 80, 20))
            health_rect.midbottom = (self.srect.centerx + 30, self.srect.top - 30)
            pygame.draw.rect(display, Colors.BLACK, health_rect)
            pygame.draw.rect(display, Colors.WHITE, (*health_rect[:2], self.hp / 100 * 80, health_rect[3]))
            pygame.draw.rect(display, Colors.WHITE, health_rect, 2)
        if ticks() - self.last_take_damage >= 400:
            self.taking_damage = False
        # rest
        if int(self.x) != self.last_x or int(self.y) != self.last_y:
            del world.enemies[(self.last_x, self.last_y)]
            world.enemies[(int(self.x), int(self.y))] = self
            self.last_x, self.last_y = int(self.x), int(self.y)
