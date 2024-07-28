import inspect

from .engine import *
from .artifacts import *
from .atoms import *
from .objects import *


class ItemTypes(Enum):
    ATOM = 0
    ARTIFACT = 1


class WorkBenchUI:
    class GridItem:
        def __init__(self, wpos, origin: Artifact | Atom, wb: super):
            self.origin = origin
            self.tex = pygame.transform.scale(
                pygame.image.load(self.origin.tex_path).convert_alpha(),
                [wb.cell_size * 1 / 2] * 2,
            )
            self.name = self.origin.name.capitalize()
            self.rect = self.tex.get_rect()
            self.wpos = wpos

        def update(self, wb: "WorkBenchUI"):
            self.rect.center = (
                wb.grid_start[0] + wb.cell_size * self.wpos[0] + wb.cell_size / 2,
                wb.grid_start[1]
                + wb.cell_size * self.wpos[1]
                + wb.cell_size / 2
                + wb.yoffset,
            )
            display.blit(self.tex, self.rect)

    def __init__(self):
        self.enabled = False

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
        if self.yoffset > 0:
            self.yoffset *= 0.6
        elif self.yoffset < 0:
            self.yoffset = 0

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
        all_items = inspect.getmembers(
            Atoms if type_ == ItemTypes.ATOM else Artifacts, inspect.isfunction
        )  # get all available atoms
        item = random.choice(all_items)[1]()
        return WorkBenchUI.GridItem(wpos, item, self)

    def update(self):
        self.set_vars()

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
                    item.update(self)

        # Lines at right and bottom of grid
        for line in self.closing_lines:
            pygame.draw.line(display, Colors.WHITE, *line)


workbench_ui = WorkBenchUI()
