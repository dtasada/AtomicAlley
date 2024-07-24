from .engine import *
from pygame.time import get_ticks as ticks


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.pos = (self.x, self.y)
        self.blit_x = self.blit_y = 0
        self.blit_pos = (self.blit_x, self.blit_y)
        self.images = {
            ("bottomleft", "bottom", "right", "topright", "top")[i]: imgload(
                "resources",
                "images",
                "player_sheet.png",
                columns=7,
                row=i,
                rows=5,
                frames=1,
            )
            for i in range(5)
        }
        self.images["left"] = [
            pygame.transform.flip(i, True, False) for i in self.images["right"]
        ]
        self.images["bottomright"] = [
            pygame.transform.flip(i, True, False) for i in self.images["bottomleft"]
        ]
        self.images["topleft"] = [
            pygame.transform.flip(i, True, False) for i in self.images["topright"]
        ]

        self.run_frames = {
            ("bottomleft", "bottom", "right", "topright", "top")[i]: imgload(
                "resources",
                "images",
                "player_sheet.png",
                columns=7,
                row=i,
                rows=5,
                start_frame=1,
                frames=6,
            )
            for i in range(5)
        }
        self.run_frames["left"] = [
            pygame.transform.flip(i, True, False) for i in self.run_frames["right"]
        ]
        self.run_frames["bottomright"] = [
            pygame.transform.flip(i, True, False) for i in self.run_frames["bottomleft"]
        ]
        self.run_frames["topleft"] = [
            pygame.transform.flip(i, True, False) for i in self.run_frames["topright"]
        ]

        self.current_frame = 0
        self.it = "bottom"
        self.image = self.images[self.it][self.current_frame]
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.srect = self.image.get_rect()
        self.yvel = 0
        self.animate_run = False
        self.dash_x = self.dash_y = 0
        self.dashing = False

    def update(self):
        self.keys()
        self.draw()

        self.blit_pos = (self.blit_x, self.blit_y)
        self.pos = (self.x, self.y)

    def scroll(self):
        game.fake_scroll[0] += (
            self.rect.centerx - game.fake_scroll[0] - WIDTH // 2
        ) * 0.1
        game.fake_scroll[1] += (
            self.rect.centery - game.fake_scroll[1] - HEIGHT // 2
        ) * 0.1
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
            self.animate_run = True
            top = True
        if keys[pygame.K_s]:
            self.animate_run = True
            bottom = True

        # self.it = image type, e.g. topleft, bottom, etc.
        xvel, yvel, it = cart_dir_to_vel(left, right, top, bottom, m=m)
        self.x += xvel
        self.y += yvel
        if it is not None:
            self.it = it

    def dash(self):
        self.dashing = True
        kwargs = {
            x: self.it == x
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
        xvel, yvel, _ = cart_dir_to_vel(**kwargs, m=2)
        self.dash_x = self.x + xvel
        self.dash_y = self.y + yvel
        self.last_shadow = 0

    def draw(self):
        if self.dashing:
            self.x += (self.dash_x - self.x) * 0.2
            self.y += (self.dash_y - self.y) * 0.2
            if self.dash_x != 0:
                diff_x = abs(self.dash_x - self.x) / self.dash_x
            else:
                diff_x = 0
            if self.dash_y != 0:
                diff_y = abs(self.dash_y - self.y) / self.dash_y
            else:
                diff_y = 0
            if ticks() - self.last_shadow >= 1:
                all_shadows.append(PlayerShadow())
                self.last_shadow = ticks()
            if diff_x <= 0.01 and diff_y <= 0.01:
                self.dash_x = self.dash_y = 0
                self.dashing = False
        #
        self.blit_x, self.blit_y = cart_to_iso(self.x, self.y, 0)
        mm_x, mm_y = cart_to_mm(self.x, self.y, 0)
        pygame.draw.rect(display, Colors.RED, (mm_x, mm_y, MMS, MMS))
        self.blit_x += S / 2
        self.blit_y += S / 4
        #
        self.blit_y += 8
        self.rect.midbottom = (self.blit_x, self.blit_y)
        self.srect.midbottom = (self.blit_x, self.blit_y)
        self.srect.x -= game.scroll[0]
        self.srect.y -= game.scroll[1]
        #
        if self.animate_run:
            if self.current_frame > len(self.run_frames[self.it]) - 1:
                self.current_frame = 0
            self.image = self.run_frames[self.it][int(self.current_frame)]
            self.current_frame += 0.15
            self.animate_run = False
        else:
            self.current_frame = 0
            self.image = self.images[self.it][int(self.current_frame)]

        if self.dash_x is None:
            image = self.image
        else:
            image = self.image
        display.blit(image, self.srect)

    def get_dir_vector(self) -> v2:
        match self.it:
            case "top":
                return (0, 1)
            case "topright":
                return (1, 1)
            case "right":
                return (1, 0)
            case "bottomright":
                return (1, -1)
            case "bottom":
                return (0, -1)
            case "bottomleft":
                return (-1, -1)
            case "left":
                return (-1, 0)
            case "topleft":
                return (-1, 1)


player = Player()


class PlayerShadow:
    def __init__(self):
        self.image = to_shadow(player.image)
        self.rect = self.image.get_rect(center=player.rect.center)
        self.srect = self.rect.copy()
        self.alpha = 255

    def update(self):
        self.alpha -= 20
        self.image.set_alpha(self.alpha)
        self.srect.x = self.rect.x - game.scroll[0]
        self.srect.y = self.rect.y - game.scroll[1]
        display.blit(self.image, self.srect)
        if self.alpha <= 0:
            all_shadows.remove(self)
