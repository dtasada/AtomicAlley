from .engine import *
from .objects import *
from .player import *

from copy import deepcopy

from enum import Enum
from typing import List
from pathlib import Path


class ArtifactInteractive(Interactive):
    def __init__(self, name, tex_path, properties: List[Effect], world_pos: v2):
        super().__init__(
            name,
            tex_path,
            world_pos,
            Interactive.MUT_PLAYER,
            Effect(Effects.INTELLIGENCE, 10),
        )
        self.name = name
        self.tex = pygame.transform.scale(
            pygame.image.load(tex_path).convert_alpha(), (SR / 8, SR / 8)
        )
        self.wpos = world_pos
        self.rect = self.tex.get_rect()
        self.properties = properties

    def update(self, player, interactives):
        super().update(player, interactives)


class ArtifactType(Enum):
    TONIC = 0
    KERNEL = 0
    DOCUMENT = 0


class Artifact:
    def __init__(self, type_: ArtifactType, name, tex_path, properties: List[Effect]):
        self.type = type_
        self.name = name
        self.tex_path = tex_path
        self.properties = properties

    def to_world(self, world_pos):
        return ArtifactInteractive(self.name, self.tex_path, self.properties, world_pos)


class Artifacts:
    @staticmethod
    def TONIC_OF_LIFE():
        return deepcopy(
            Artifact(
                ArtifactType.TONIC,
                "Tonic of Life",
                Path("resources", "images", "artifacts", "tonic.png"),
                [Effect(Effects.HEALTH, 100)],
            )
        )

    @staticmethod
    def KERNEL_OF_IDEOLOGY():
        return deepcopy(
            Artifact(
                ArtifactType.KERNEL,
                "Kernel of Ideology",
                Path("resources", "images", "artifacts", "kernel.png"),
                [Effect(Effects.INTELLIGENCE, 100)],
            )
        )
