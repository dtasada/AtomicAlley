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
            self.text_rect = self.text_image.get_rect()

        def update(self):
            self.cell_topleft = (
                self.wb.grid_start[0] + self.wb.cell_size * self.wpos[0],
                self.wb.grid_start[1]
                + self.wb.cell_size * self.wpos[1]
                + self.wb.yoffset,
            )
            self.rect.center = (
                self.cell_topleft[0] + self.wb.cell_size / 2,
                self.cell_topleft[1] + self.wb.cell_size / 2,
            )
            display.blit(self.image, self.rect)

        def draw_text(self):
            mp = pygame.mouse.get_pos()
            if pygame.Rect(self.cell_topleft, [self.wb.cell_size] * 2).collidepoint(mp):
                self.text_rect.topleft = mp
                display.blit(self.text_image, self.text_rect)

    def __init__(self):
        self.enabled = False
        self.master_rect = None

        self.outer_margin = (202, 128)
        self.inner_margin = 32
        self.grid_size = (4, 4)

        self.yoffset = 0
        self.set_vars()

        # WorkBenchUI.items is a grid of 4x4, each of which contains None, or a selection of atoms or Artifacts
        self.items: List[List[WorkBenchUI.GridItem | None]] = [
            [None] * self.grid_size[1]
        ] * self.grid_size[0]
        self.gen_grid()

    def enable(self):
        self.enabled = True
        self.gen_grid()

    def disable(self):
        self.enabled = False

    def set_vars(self):
        if self.master_rect:
            if self.enabled:
                self.yoffset = 0 if self.yoffset < 0 else self.yoffset * 0.6
            else:
                if self.yoffset < self.master_rect.bottom:
                    if self.yoffset == 0:
                        self.yoffset = 10
                    self.yoffset /= 0.6

        self.master_rect = pygame.Rect(
            self.outer_margin[0],
            self.outer_margin[1] + self.yoffset,
            display.width - self.outer_margin[0] * 2,
            display.height - self.outer_margin[1] * 2,
        )

        self.cell_size = (
            self.master_rect.height - self.inner_margin * 2
        ) / self.grid_size[1]

        self.grid_start = (
            self.master_rect.left + self.inner_margin,
            self.master_rect.top + self.inner_margin + self.yoffset,
        )
        self.grid_end = (
            self.grid_start[0] + self.grid_size[0] * self.cell_size,
            self.grid_start[1] + self.grid_size[1] * self.cell_size + self.yoffset,
        )

        # Lines at right and bottom of grid
        self.closing_lines = (
            (
                (self.grid_start[0], self.grid_end[1] + self.yoffset),
                (self.grid_end[0], self.grid_end[1] + self.yoffset),
            ),
            (
                (self.grid_end[0], self.grid_start[1] + self.yoffset),
                (self.grid_end[0], self.grid_end[1] + self.yoffset),
            ),
        )

    def gen_grid(self) -> None:
        "Generates the workbench inventory (in-place)"
        for y, row in enumerate(self.items):
            for x, _ in enumerate(row):
                if random.randint(1, 16) < 4:  # 1 in 4 chance for an item
                    self.items[y][x] = self.random_item(
                        (x, y),
                        (
                            ItemTypes.ARTIFACT  # 1 in 8 chance for an artifact
                            if random.randint(1, 8) == 1
                            else ItemTypes.ATOM
                        ),
                    )

        self.yoffset = self.master_rect.bottom

    def random_item(self, wpos: v2, type_: ItemTypes) -> GridItem:
        type_ = Atoms if type_ == ItemTypes.ATOM else Artifacts
        all_items = [var for var in vars(type_) if not var.startswith("__")]
        item = getattr(type_, random.choice(all_items))
        return WorkBenchUI.GridItem(wpos, item, self)

    def update(self):
        self.set_vars()

        if not self.enabled and self.yoffset == self.master_rect.bottom:
            return

        pygame.draw.rect(
            display, Colors.GRAYS[40], self.master_rect, border_radius=BORDER_RADIUS
        )

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

                if item:
                    item.update()

        for _, row in enumerate(self.items):
            for _, item in enumerate(row):
                if item:
                    item.draw_text()

        # Lines at right and bottom of grid
        for line in self.closing_lines:
            pygame.draw.line(display, Colors.WHITE, *line)


workbench_ui = WorkBenchUI()
