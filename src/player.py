from .engine import *
from .artifacts import *


class Player:
    def __init__(self):
        # self.x = 0
        # self.y = 0
        self.mmrect = pygame.FRect((0, 0, 20, 20))
        self.wpos = (self.x, self.y)
        self.blit_x = self.blit_y = 0
        self.dpos = (self.blit_x, self.blit_y)
        self.images = {
            ("bottomleft", "bottom", "right", "topright", "top")[i]: imgload(
                "resources",
                "images",
                "player",
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
        self.check_rects = []
        self.run_frames = {
            ("bottomleft", "bottom", "right", "topright", "top")[i]: imgload(
                "resources",
                "images",
                "player",
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
        self.last_dash = ticks()
        self.dash_time = 1320

        # self.hotbar = [Tonic("Ar"), Tonic("Si")]
        self.hotbar = [
            Artifacts.ARSENIC.to_hotbar(),
            Artifacts.BISMUTH.to_hotbar(),
        ]
        # wat is dit voor rust ass looking code
        # dit is python
        self.show_hotbar = False
        self.hotbar_image = imgload("resources", "images", "hotbar.png")
        self.selected_image = imgload("resources", "images", "selected.png")
        self.unavailable_image = imgload("resources", "images", "unavailable.png")
        self.selected = 0
        self.hotbar_length = 9
        self.hotbar_rect = self.hotbar_image.get_rect(topleft=(display.width + 10, 80))

        # abilities
        self.show_abilities = False
        self.black_surf = pygame.Surface(display.size)
        self.black_surf.set_alpha(0)
        self.abilities = []
    
    @property
    def x(self):
        return self.mmrect.x / game.rect_scale

    @x.setter
    def x(self, value):
        self.mmrect.x = value * game.rect_scale

    @property
    def y(self):
        return self.mmrect.y / game.rect_scale
    
    @y.setter
    def y(self, value):
        self.mmrect.y = value * game.rect_scale

    def update(self):
        if game.state == States.PLAY and not game.dialogue:
            self.keys()
        self.draw()

        self.dpos = (self.blit_x, self.blit_y)
        self.wpos = (self.x, self.y)

    def scroll(self):
        game.fake_scroll[0] += (
            self.rect.centerx - game.fake_scroll[0] - display.width // 2
        ) * 0.1
        game.fake_scroll[1] += (
            self.rect.centery - game.fake_scroll[1] - display.height // 2
        ) * 0.1
        game.scroll[0] = int(game.fake_scroll[0])
        game.scroll[1] = int(game.fake_scroll[1])

    def handle_keypress(self, event):
        if event.key == pygame.K_SPACE:
            if ticks() - self.last_dash >= self.dash_time or True:
                self.dash()
        
        elif event.key == pygame.K_i:
            if not self.show_abilities:
                self.show_hotbar = not self.show_hotbar
        
        elif event.key == pygame.K_o:
            if not self.show_hotbar:
                self.show_abilities = not self.show_abilities
        
        elif event.key == pygame.K_LEFT:
            self.selected -= 1
            if self.selected < 0:
                self.selected = self.hotbar_length - 1
        
        elif event.key == pygame.K_RIGHT:
            self.selected += 1
            if self.selected > self.hotbar_length - 1:
                self.selected = 0

    def keys(self):
        keys = pygame.key.get_pressed()
        m = 0.08
        left = right = top = bottom = False
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
        if not self.dashing:
            xvel, yvel, it = cart_dir_to_vel(left, right, top, bottom, m=m)
            self.x += xvel
            for cr in self.check_rects:
                if self.mmrect.colliderect(cr):
                    if xvel > 0:
                        self.mmrect.right = cr.left
                    else:
                        self.mmrect.left = cr.right
            self.y += yvel
            for cr in self.check_rects:
                if self.mmrect.colliderect(cr):
                    if yvel > 0:
                        self.mmrect.bottom = cr.top
                    else:
                        self.mmrect.top = cr.bottom
            if it is not None:
                self.it = it

        # hotbar
        m = 0.2
        if not self.show_hotbar:
            self.hotbar_rect.left += (display.width + 10 - self.hotbar_rect.left) * m
        else:
            self.hotbar_rect.centerx += (
                display.width / 2 - self.hotbar_rect.centerx
            ) * m

        display.blit(self.hotbar_image, self.hotbar_rect)
        for x, artifact in enumerate(self.hotbar):
            artifact_rect = pygame.Rect(
                self.hotbar_rect.x + R + 39 * x * R,
                self.hotbar_rect.y + R,
                *artifact.image.size,
            )
            display.blit(artifact.image, artifact_rect)
            if artifact_rect.collidepoint(pygame.mouse.get_pos()):
                xor = pygame.mouse.get_pos()[0] + 5
                yor = pygame.mouse.get_pos()[1] + 80
                # xor and yor are the x and y origin, not the xor operator
                y = 0
                for atom in artifact.origin.reagents:
                    for prop in atom.properties:
                        if prop.mag_type == MagType.REL_COEF:
                            mag = str((prop.magnitude * 100) if prop.magnitude < 0 else ("+" + str(prop.magnitude * 100))) + "%"
                            if prop.type == Properties.MUT_ALL_STATS:
                                type_ = "on all stats"
                            else:
                                type_ = prop.type.name.lower().replace("_", " ")
                            prop_text = f"{mag} {type_}"
                        elif prop.mag_type == MagType.SET_ABS:
                            if prop.type == Properties.TRADE_FOR_CHOICES:
                                prop_text = f"Can be traded for {prop.magnitude} random elements"
                        else:
                            prop_text = "asd"
                        write(
                            display,
                            "topleft",
                            prop_text,
                            fonts[24],
                            Colors.GREEN if prop.magnitude > 0 else Colors.RED,
                            xor,
                            yor + y,
                        )
                        y += 34

        # abilities
        if self.show_abilities:
            self.black_surf.set_alpha(
                self.black_surf.get_alpha() + (60 - self.black_surf.get_alpha()) * 0.2
            )
        else:
            self.black_surf.set_alpha(
                self.black_surf.get_alpha() + (0 - self.black_surf.get_alpha()) * 0.2
            )

    def get_collisions(self):
        return

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
        xvel, yvel, _ = cart_dir_to_vel(**kwargs, m=4)
        self.dash_x = self.x + xvel
        self.dash_y = self.y + yvel
        self.last_shadow = 0
        self.last_dash = ticks()

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
        # pygame.draw.rect(display, Colors.RED, self.mmrect)
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
            if self.current_frame >= len(self.run_frames[self.it]):
                self.current_frame = 0
            self.image = self.run_frames[self.it][int(self.current_frame)]
            self.current_frame += 0.14
            self.animate_run = False
        else:
            self.current_frame = 0
            self.image = self.images[self.it][int(self.current_frame)]

        display.blit(self.image, self.srect)
        #
        if ticks() - self.last_dash >= self.dash_time:
            p = Particle(self.srect.centerx, self.srect.top + 12)
            all_particles.append(p)

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
