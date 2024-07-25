from .engine import *
from .uis import *
from .artifacts import *

import inspect


class ItemTypes(Enum):
    ATOM = 0
    ARTIFACT = 1


class GridItem:
    def __init__(
        self,
        type_,
        wpos,
        origin: Artifact,  # origin artifact/atom
    ):
        self.type = type_
        self.tex = pygame.transform.scale(
            pygame.image.load(origin.tex_path).convert_alpha(), (GRID_SIZE, GRID_SIZE)
        )
        self.name = self.type.name.capitalize()
        self.rect = self.tex.get_rect()
        self.wpos = wpos
        self.dpos = (0, 0)
        self.origin = origin

    @staticmethod
    def gen_random(wpos: v2, type_: ItemTypes):
        match type_:
            case ItemTypes.ATOM:
                pass
            case ItemTypes.ARTIFACT:
                all_artifacts = inspect.getmembers(
                    Artifacts, inspect.isfunction
                )  # get all available artifacts
                artifact = random.choice(all_artifacts)[1]()
                return __class__(artifact.type, wpos, artifact)

    def update(self):
        display.blit(self.tex, self.rect)
