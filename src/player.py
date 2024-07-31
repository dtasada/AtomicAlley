from .engine import *
from .artifacts import *


class PlayerAbilityTypes(Enum):
    SLASH = 0
    DASH = 1


class PlayerAbility:
    ability_sprs = imgload("resources", "images", "abilities.png", columns=2)
    def __init__(self, type_, text, needed):
        self.type_ = type_
        self.text = text
        self.needed = needed
        self.image = PlayerAbility.ability_sprs[self.type_.value]


class Player(Smart):
    def __init__(self):
        # properties
        self.OG_CRIT_CHANCE = 0.1
        self.OG_DAMAGE = 10
        self.OG_DASH_COOLDOWN = 1320
        self.OG_DASH_DAMAGE = 5
        self.OG_DASH_RANGE = 2
        self.OG_MAX_HEALTH = 50
        self.OG_MOVEMENT_SPEED = 0.08
        #
        self.update_properties()
        # rest
        self.mmrect = pygame.FRect((0, 0, 20, 20))
        self.wpos = (self.x, self.y)
        self.blit_x = self.blit_y = 0
        self.dpos = (self.blit_x, self.blit_y)
        self.images = {
            Weapons.HANDS:
            {
                ("bottomleft", "bottom", "right", "topright", "top")[i]: image
                for i, image in enumerate(
                    imgload(
                        "resources",
                        "images",
                        "player",
                        "player_sheet.png",
                        rows=5,
                    )
                )
            },
            Weapons.BAT:
            {
                ("bottomleft", "bottom", "right", "topright", "top", "bottomright", "topleft", "left")[i]: image
                for i, image in enumerate(
                imgload(
                    "resources",
                    "images",
                    "player",
                    "player_bat_sheet.png",
                    rows=8,
                    )
                )
            }
        }

        self.run_frames = {
            Weapons.HANDS:
            {
                ("bottomleft", "bottom", "right", "topright", "top")[i]: row
                for i, row in enumerate(
                    imgload(
                        "resources",
                        "images",
                        "player",
                        "player_run_sheet.png",
                        rows=5,
                        columns=6,
                    )
                )
            },
            Weapons.BAT:
            {
                ("bottomleft", "bottom", "right", "topright", "top", "bottomright", "topleft", "left")[i]: row
                for i, row in enumerate(
                    imgload(
                        "resources",
                        "images",
                        "player",
                        "player_bat_run_sheet.png",
                        rows=8,
                        columns=6,
                    )
                )
            }
        }

        for weapon in Weapons:
            if weapon != Weapons.BAT:
                self.images[weapon]["left"] = pygame.transform.flip(self.images[weapon]["right"], True, False) 
                
                self.images[weapon]["bottomright"] = pygame.transform.flip(self.images[weapon]["bottomleft"], True, False) 
                
                self.images[weapon]["topleft"] = pygame.transform.flip(self.images[weapon]["topright"], True, False) 

                self.run_frames[weapon]["left"] = [
                    pygame.transform.flip(i, True, False) for i in self.run_frames[weapon]["right"]
                ]
                self.run_frames[weapon]["bottomright"] = [
                    pygame.transform.flip(i, True, False) for i in self.run_frames[weapon]["bottomleft"]
                ]
                self.run_frames[weapon]["topleft"] = [
                    pygame.transform.flip(i, True, False) for i in self.run_frames[weapon]["topright"]
                ]

        self.weapon = Weapons.BAT
        self.current_frame = 0
        self.it = "bottom"
        self.image = self.images[self.weapon][self.it]
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.srect = self.image.get_rect()
        self.yvel = 0
        self.animate_run = False
        self.dash_x = self.dash_y = 0
        self.dashing = False
        self.last_dash = ticks()
        self.hotbar = [
            Artifacts.ARSENIC_FIZZ.to_hotbar(),
        ]
        self.inventory = [None for _ in range(16)]
        self.show_hotbar = False
        self.hotbar_image = imgload("resources", "images", "hotbar.png")
        self.inventory_image = imgload("resources", "images", "inventory.png")
        self.selected_image = imgload("resources", "images", "selected.png")
        self.unavailable_image = imgload("resources", "images", "unavailable.png")
        self.selected = 0
        self.hotbar_length = 9
        self.hotbar_rect = self.hotbar_image.get_rect(topleft=(display.get_width() + 10, 10))
        self.inventory_rect = self.inventory_image.get_rect(topleft=(display.get_width() + 10, display.get_height() / 2 + 60))

        # abilities
        self.show_abilities = False
        self.black_surf = pygame.Surface(display.get_size())
        self.black_surf.set_alpha(0)
        self.red_surf = pygame.Surface(display.get_size())
        self.red_surf.fill(Colors.RED)
        self.red_surf.set_alpha(100)
        self.abilities = [
            PlayerAbility(PlayerAbilityTypes.SLASH, "Your basic weapon, your swinging bat.\nLeft click to use.\nUpgradable with tonics.", None),
            PlayerAbility(PlayerAbilityTypes.DASH, "Dashes towards character direction.\nSpacebar to use.", None),
        ]
        self.black_stripe = pygame.Surface((display.get_width(), 500))
        self.black_stripe.set_alpha(120)
        self.black_stripe_rect = self.black_stripe.get_rect(topleft=(display.get_width() + 10, 100))
        # slash
        self.slash_sprs = imgload("resources", "images", "player", "player_slash_spritesheet.png", columns=5, scale=4)
        self.slash_rect = self.slash_sprs[0].get_rect()
        self.last_slash = ticks()
        self.slash_cooldown = 800
        self.slash_index = 0
        self.slashing = False
        self.slash_direc = None
        # hp
        self.hp = self.MAX_HEALTH
        self.health_sprs = imgload("resources", "images", "player", "player_health.png", columns=15, scale=8)
        self.health_rect = self.health_sprs[0].get_rect()
        self.last_take_damage = ticks()
        self.taking_damage = False

    def update(self):
        self.update_properties()
        if game.state == States.PLAY and not game.dialogue:
            self.keys()
        self.draw()

        self.dpos = (self.blit_x, self.blit_y)
        self.wpos = (self.x, self.y)
    
    def take_damage(self, damage):
        self.hp -= damage
        self.last_take_damage = ticks()
        self.taking_damage = True
    
    def new_inventory_item(self, item):
        if self.inventory.count(None) == 0:
            return
        inv_item = item.origin.to_inventory()
        item.kill()
        for i, v in enumerate(self.inventory):
            if v is None:
                self.inventory[i] = inv_item
                break
        
    def scroll(self):
        game.fake_scroll[0] += (
            self.rect.centerx - game.fake_scroll[0] - display.get_width() // 2
        ) * 0.1
        game.fake_scroll[1] += (
            self.rect.centery - game.fake_scroll[1] - display.get_height() // 2
        ) * 0.1
        game.scroll[0] = int(game.fake_scroll[0])
        game.scroll[1] = int(game.fake_scroll[1])

    def process_event(self, workbench_ui, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if ticks() - self.last_dash >= self.DASH_COOLDOWN:
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
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # slash
            if not self.slashing:
                if ticks() - self.last_slash >= self.slash_cooldown:
                    self.slashing = True
                    self.last_slash = ticks()
                    self.slash_direc = self.it
                    game.screen_shake(7, 100)
            # workbench
            if workbench_ui.enabled:
                for i, v in enumerate(self.inventory):
                    if v is not None:
                        if v.artifact_rect.collidepoint(event.pos):
                            self.inventory[i] = None
                            workbench_ui.glass = v
                # concoct final
                if workbench_ui.glass is not None:
                    if workbench_ui.concoct_rect.collidepoint(event.pos):
                        reagents = [getattr(Atoms, sel.name.upper()) for sel in workbench_ui.get_selected]
                        tonic = Artifact(
                            ArtifactType.TONIC,
                            atom_images[6],
                            "asd",
                            reagents=reagents,
                        ).to_hotbar()
                        self.hotbar.append(tonic)
                        workbench_ui.glass = None
                        
    def keys(self):
        keys = pygame.key.get_pressed()
        m = self.MOVEMENT_SPEED
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
    
    def damage_cooldown(self):
        if self.taking_damage:
            if ticks() - self.last_take_damage <= 200:
                display.blit(self.red_surf, (0, 0))
            if ticks() - self.last_take_damage >= 500:
                self.taking_damage = False

    def render_hotbar(self):
        # hotbar
        m = 0.2
        if not self.show_hotbar:
            d = (display.get_width() + 10 - self.hotbar_rect.left) * m
            bsd = (display.get_width() + 10 - self.black_stripe_rect.left) * m
            ind = (display.get_width() + 120 - self.inventory_rect.centerx) * m
        else:
            d = (display.get_width() / 2 - self.hotbar_rect.centerx) * m
            bsd = (0 - self.black_stripe_rect.left) * m
            ind = (display.get_width() / 2 + 254 - self.inventory_rect.centerx) * m
        self.hotbar_rect.centerx += d
        self.inventory_rect.centerx += ind
        self.black_stripe_rect.left += bsd

        # display.blit(self.black_stripe, self.black_stripe_rect)
        display.blit(self.hotbar_image, self.hotbar_rect)
        display.blit(self.inventory_image, self.inventory_rect)
        for x, artifact in enumerate(self.hotbar):
            artifact_rect = pygame.Rect(
                self.hotbar_rect.x + R + 39 * x * R,
                self.hotbar_rect.y + R,
                *artifact.image.get_size(),
            )
            display.blit(artifact.image, artifact_rect)
            # MULTS EVERYONE CALM DOWN
            if artifact_rect.collidepoint(pygame.mouse.get_pos()):
                # xor and yor are the x and y origin, not the xor operator
                xor = pygame.mouse.get_pos()[0] + 5  
                yor = pygame.mouse.get_pos()[1] + 80
                # multipliers (sorry)
                y = 0
                for atom in artifact.origin.reagents:
                    for prop in atom.properties:
                        prop_text = "Other secret ability"
                        if prop.mag_type == MagType.REL_COEF:
                            mag = (
                                str(
                                    (prop.magnitude * 100)
                                    if prop.magnitude < 0
                                    else ("+" + str(prop.magnitude * 100))
                                )
                                + "%"
                            )
                            type_ = prop.type.name.lower().replace("_", " ")
                            prop_text = f"{mag} {type_}"
                        elif prop.mag_type == MagType.SET_ABS:
                            if prop.type == Properties.TRADE_FOR_CHOICES:
                                prop_text = f"Can be traded for {prop.magnitude} random elements"
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
            
        # render inventory
        yo = 0
        xo = 0
        for artifact in self.inventory:
            if artifact is None:
                continue
            artifact_rect = pygame.Rect(
                self.inventory_rect.x + R + 19 * R * xo,
                self.inventory_rect.y + R + 19 * R * yo,
                18 * R,
                18 * R
            )
            xo += 1
            if xo % 4 == 0:
                yo += 1
                xo = 0
            img = pygame.transform.scale(artifact.image, artifact_rect.size)
            display.blit(img, artifact_rect)
            artifact.artifact_rect = artifact_rect
            if artifact_rect.collidepoint(pygame.mouse.get_pos()):
                write(display, "topleft", artifact.name.replace("_", " "), fonts[20], Colors.WHITE, *pygame.mouse.get_pos())

        # abilities
        if self.show_abilities:
            self.black_surf.set_alpha(
                self.black_surf.get_alpha() + (80 - self.black_surf.get_alpha()) * 0.1
            )
        else:
            self.black_surf.set_alpha(
                self.black_surf.get_alpha() + (0 - self.black_surf.get_alpha()) * 0.2
            )
        
    def update_properties(self):
        # mults
        for prop in Properties:
            if prop.value != 7:
                setattr(self, prop.name, getattr(self, "OG_" + prop.name))

        mults = {p.name: 1 for p in Properties}
        if not hasattr(self, "hotbar"):
            return
        for artifact in self.hotbar:
            for atom in artifact.origin.reagents:
                for prop in atom.properties:
                    if prop.mag_type == MagType.REL_COEF:
                        mults[prop.type.name] += prop.magnitude
        for name, mult in mults.items():
            try:
                cur = getattr(self, name)
            except AttributeError:
                pass
            setattr(self, name, cur * mult)
        self.hp = min(self.hp, self.MAX_HEALTH)
        
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
        xvel, yvel, _ = cart_dir_to_vel(**kwargs, m=self.DASH_RANGE)
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
            if self.current_frame >= len(self.run_frames[self.weapon][self.it]):
                self.current_frame = 0
            self.image = self.run_frames[self.weapon][self.it][int(self.current_frame)]
            self.current_frame += 0.14
            self.animate_run = False
        else:
            self.current_frame = 0
            self.image = self.images[self.weapon][self.it]

        display.blit(self.image, self.srect)
        self.health_rect.midbottom = (display.width / 2, display.height - 30)
        index = int((1 - (self.hp / self.MAX_HEALTH)) * 15)
        display.blit(self.health_sprs[index], self.health_rect)
        write(display, "midbottom", f"max health: {self.MAX_HEALTH}", fonts[16], Colors.WHITE, display.width / 2, display.height - 4)
        #
        if ticks() - self.last_dash >= self.DASH_COOLDOWN:
            p = Particle(self.srect.centerx, self.srect.top + 12)
            all_particles.append(p)
        # slashing
        if self.slashing:
            self.slash_index += 0.6
            try:
                self.slash_sprs[int(self.slash_index)]
            except IndexError:
                self.slashing = False
                self.slash_index = 0
            else:
                center = [self.srect.centerx, self.srect.centery]
                t = 80
                if "left" in self.slash_direc:
                    center[0] -= t
                if "right" in self.slash_direc:
                    center[0] += t
                if "top" in self.slash_direc:
                    center[1] -= t
                if "bottom" in self.slash_direc:
                    center[1] += t * 0.4
                slash_img = self.slash_sprs[int(self.slash_index)]
                if "left" in self.slash_direc:
                    slash_img = pygame.transform.flip(slash_img, True, False)
                # slash_img = pygame.transform.scale_by(slash_img, 1.4)
                self.slash_rect.center = center
                display.blit(slash_img, self.slash_rect)
                # pygame.draw.rect(display, Colors.WHITE, self.slash_rect, 5)
        self.damage_cooldown()

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


class DamageIndicator:
    def __init__(self, damage, nature, enemy, crit=False):
        self.crit = crit
        self.damage = damage
        self.image = fonts[40].render(str(damage), True, Colors.WHITE if nature else Colors.RED)
        self.xo = rand(-40, 40)
        self.yo = -80
        self.yvel = -1.5
        self.rect = self.image.get_frect()
        self.enemy = enemy
        self.last_spawned = ticks()
    
    def update(self):
        self.draw()

    def draw(self):
        rgb_color = [(sin((ticks() * 0.01) + x) + 1) * 0.5 * 255 for x in range(3)]
        if self.crit:
            self.image = fonts[50].render(str(self.damage), True, rgb_color)
        if self.damage == "KO!":
            self.image = fonts[50].render("KO!", True, rgb_color)
        self.rect.center = (self.enemy.srect.centerx + self.xo, self.enemy.srect.top + self.yo)
        self.yo += self.yvel
        if ticks() - self.last_spawned >= 1000:
            self.image.set_alpha(self.image.get_alpha() - 10)
            if self.image.get_alpha() <= 0:
                all_particles.remove(self)
        self.rect.y += self.yvel
        display.blit(self.image, self.rect)
