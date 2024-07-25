from .engine import *
from .artifacts import *
from .objects import *
from .griditem import *


class WorkBenchUI:
    def __init__(self):
        self.margin = 128
        self.master_rect = pygame.Rect(
            self.margin,
            self.margin,
            display.width - self.margin * 2,
            display.height - self.margin * 2,
        )

        # WorkBenchUI.items is a grid of 4x4, each of which contains None, or a selection of atoms or Artifacts
        self.items = self.gen_grid()
        print("items", self.items)

    def gen_grid(self) -> List[List[GridItem]]:
        l = [[None] * 4] * 4

        for y, row in enumerate(l):
            for x, _ in enumerate(row):
                l[y][x] = GridItem.gen_random(
                    (x, y),
                    (
                        ItemTypes.ARTIFACT
                        if random.randint(1, 10) == 1
                        else ItemTypes.ATOM
                    ),
                )

        return l

    def update(self):
        pygame.draw.rect(
            display, Colors.GRAYS[40], self.master_rect, border_radius=BORDER_RADIUS
        )


workbench_ui = WorkBenchUI()
