from __future__ import annotations

from .engine import *
from .artifacts import *
from .atoms import *
from .objects import *


class ItemTypes(Enum):
    ATOM = 0
    ARTIFACT = 1


class WorkBenchUI:
    class GridItem:
        def __init__(self, wpos, origin: Artifact | Atom, wb: WorkBenchUI):
            self.origin = origin
            self.wb = wb

            self.wpos = wpos
            self.name = self.origin.name.capitalize()

            self.image = pygame.transform.scale(
                self.origin.image,
                [wb.cell_size * 1 / 2] * 2,
            )
            self.rect = self.image.get_rect()
            self.cell_topleft = None
            self.text_image = fonts[FontSize.SMALL].render(
                self.name, ANTI_ALIASING, Colors.WHITE
            )
            self.shadow_text_image = fonts[FontSize.SMALL].render(
                "Shadowed " + self.name, ANTI_ALIASING, Colors.WHITE
            )
            self.text_rect = self.text_image.get_rect()
            self.selected = False
            # shadow
            self.shadow = rand(1, 1) == 1
            self.shadow_image = self.image.copy()
            for y in range(self.shadow_image.get_height()):
                for x in range(self.shadow_image.get_width()):
                    if self.image.get_at((x, y)) != (0, 0, 0, 0):
                        if rand(1, 4) == 1:
                            self.shadow_image.set_at((x, y), [rand(0, 255) for _ in range(3)])
            
        def process_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.selected:
                            self.selected = False
                        else:
                            if self.wb.selected_index < 3:
                                self.selected = True

        def update(self):
            img = self.image if not self.shadow else self.shadow_image
            self.cell_topleft = (
                self.wb.grid_start[0] + self.wb.cell_size * self.wpos[0],
                self.wb.grid_start[1] + self.wb.cell_size * self.wpos[1]
            )
            if not self.selected:
                self.rect.center = (
                    self.cell_topleft[0] + self.wb.cell_size / 2,
                    self.cell_topleft[1] + self.wb.cell_size / 2,
                )
                display.blit(img, self.rect)
            else:
                self.wb.selected_index += 1
                self.rect.center = (
                    self.wb.master_rect.x + self.wb.master_rect.width / 2 + self.wb.selected_index * (self.wb.master_rect.width / 8) + 38,
                    self.wb.master_rect.y + self.wb.master_rect.height / 2 - 50
                )
                display.blit(img, self.rect)
                if (self.wb.num_selected > 1 and self.wb.selected_index == 1) or (self.wb.num_selected in (1, 3) and self.wb.selected_index == 2):
                    write(display, "center", "+", fonts[50], Colors.WHITE, self.wb.master_rect.x + self.wb.master_rect.width / 2 + self.wb.selected_index * (self.wb.master_rect.width / 8) + 95, self.wb.master_rect.y + self.wb.master_rect.height / 2 - 50)

        def draw_text(self):
            mp = pygame.mouse.get_pos()
            if self.rect.collidepoint(mp):
                self.text_rect.topleft = mp
                display.blit(self.text_image if not self.shadow else self.shadow_text_image, self.text_rect)

    def __init__(self):
        self.enabled = False
        self.master_rect = None

        self.outer_margin = (202, 128)
        self.inner_margin = 32
        self.grid_size = (4, 4)

        self.master_rect = pygame.Rect(
            self.outer_margin[0],
            self.outer_margin[1],
            display.get_width() - self.outer_margin[0] * 2,
            display.get_height() - self.outer_margin[1] * 2 + 80,
        )
        self.set_vars()

        self.selected_items = []
        self.gen_grid()
        self.empty_glass_image = imgload("resources", "images", "empty_glass.png")
        self.empty_glass_rect = self.empty_glass_image.get_rect(center=(860, 225))
        self.glass = None
        # concocts button
        self.concoct_image = pygame.Surface((160, 70))
        self.concoct_image.fill(Colors.GRAYS[90])
        pygame.draw.rect(self.concoct_image, Colors.GRAYS[230], (0, 0, *self.concoct_image.get_size()), 4)
        write(self.concoct_image, "center", "concoct!", fonts[30], Colors.WHITE, *[s / 2 for s in self.concoct_image.get_size()])
        self.concoct_rect = self.concoct_image.get_rect()
    
    @property
    def num_selected(self):
        return len(self.get_selected)

    @property
    def get_selected(self):
        return [item for row in self.items for item in row if item is not None and item.selected]

    def enable(self):
        self.enabled = True
        self.gen_grid()

    def disable(self):
        self.enabled = False

    def set_vars(self):
        yoffset = (display.get_height() / 2 + 60) if self.enabled else (display.get_height() + 300)
        self.master_rect.centery += (yoffset - self.master_rect.centery) * 0.6

        self.cell_size = (
            self.master_rect.height - self.inner_margin * 2
        ) / self.grid_size[1]

        self.grid_start = (
            self.master_rect.left + self.inner_margin,
            self.master_rect.top + self.inner_margin + 0,
        )
        self.grid_end = (
            self.grid_start[0] + self.grid_size[0] * self.cell_size,
            self.grid_start[1] + self.grid_size[1] * self.cell_size + 0,
        )

        # Lines at right and bottom of grid
        self.closing_lines = (
            (
                (self.grid_start[0], self.grid_end[1] + 0),
                (self.grid_end[0], self.grid_end[1] + 0),
            ),
            (
                (self.grid_end[0], self.grid_start[1] + 0),
                (self.grid_end[0], self.grid_end[1] + 0),
            ),
        )

    def gen_grid(self) -> None:
        "Generates the workbench inventory (in-place)"
        self.items = [[None for x in range(4)] for y in range(4)]
        for y in range(len(self.items)):
            for x in range(len(self.items[0])):
                if rand(1, 4) == 1:
                    # make it an atom
                    self.items[y][x] = self.random_item(
                        (x, y),
                        ItemTypes.ATOM
                    )

    def random_item(self, wpos: v2, type_: ItemTypes) -> GridItem:
        type_ = Atoms if type_ == ItemTypes.ATOM else Artifacts
        all_items = [var for var in vars(type_) if not var.startswith("__")]
        item = getattr(type_, random.choice(all_items))
        return WorkBenchUI.GridItem(wpos, item, self)

    def update(self):
        self.set_vars()

        pygame.draw.rect(
            display, Colors.GRAYS[40], self.master_rect, border_radius=BORDER_RADIUS
        )
        pygame.draw.rect(
            display, Colors.WHITE, self.master_rect, 2, border_radius=BORDER_RADIUS
        )
        # helping information
        write(display, "topleft", "you can also drop items from your inventory", fonts[16], Colors.WHITE, self.master_rect.x + 8, self.master_rect.y + 6)

        # render the items on the grid
        self.selected_index = 0
        for y, row in enumerate(self.items):
            pygame.draw.line(
                display,
                Colors.WHITE,
                (self.grid_start[0], self.grid_start[1] + self.cell_size * y),
                (self.grid_end[0], self.grid_start[1] + self.cell_size * y),
            )
            for x, item in enumerate(row):
                pygame.draw.line(
                    display,
                    Colors.WHITE,
                    (self.grid_start[0] + self.cell_size * x, self.grid_start[1]),
                    (self.grid_start[0] + self.cell_size * x, self.grid_end[1]),
                )
                if item is not None:
                    item.update()
        # selected grid
        # pygame.draw.line(
        #     display,
        #     Colors.WHITE,
        #     (self.master_rect.x + self.master_rect.width / 2 + 40, self.master_rect.y + self.master_rect.height / 2 - 70),
        #     (self.master_rect.right - 50, self.master_rect.y + self.master_rect.height / 2 - 70),
        # )
        # pygame.draw.line(
        #     display,
        #     Colors.WHITE,
        #     (self.master_rect.x + self.master_rect.width / 2 + 40, self.master_rect.y + self.master_rect.height / 2 + 10),
        #     (self.master_rect.right - 50, self.master_rect.y + self.master_rect.height / 2 + 10),
        # )

        for row in self.items:
            for item in row:
                if item:
                    item.draw_text()

        # Lines at right and bottom of grid
        for line in self.closing_lines:
            pygame.draw.line(display, Colors.WHITE, *line)
        
        # empty glass indicator
        xo, yo = self.master_rect.topleft
        self.empty_glass_rect.midtop = (xo + self.master_rect.width / 4 * 3 - 58, yo + 40)
        if self.glass is None:
            display.blit(self.empty_glass_image, self.empty_glass_rect)
            if self.empty_glass_rect.collidepoint(pygame.mouse.get_pos()):
                write(display, "topleft", "*insert glass*", fonts[FontSize.SMALL], Colors.WHITE, *pygame.mouse.get_pos())
        else:
            display.blit(self.glass.image, self.empty_glass_rect)
            if self.empty_glass_rect.collidepoint(pygame.mouse.get_pos()):
                write(display, "topleft", self.glass.name.replace("_", " "), fonts[FontSize.SMALL], Colors.WHITE, *pygame.mouse.get_pos())
        # concoct button
        if self.glass is not None and self.num_selected >= 1:
            self.concoct_rect.topleft = (
                self.empty_glass_rect.x + 92,
                self.empty_glass_rect.y + 14
            )
            display.blit(self.concoct_image, self.concoct_rect)

workbench_ui = WorkBenchUI()
