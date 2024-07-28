from __future__ import annotations, absolute_import
from .engine import *
from .objects import *
from .atoms import *

from copy import deepcopy

from enum import Enum
from typing import List
from pathlib import Path


"""
nee maar als je 235 classes nodig hebt voor een potion dan gaat er iets mis
"""


class ArtifactInteractive(Interactive):
    "Artifact class for floor drops"

    def __init__(self, origin: Artifact, world_pos: v2):
        super().__init__(
            origin.name,
            origin.tex_path,
            world_pos,
            Interactive.MUT_PLAYER,
            [atom.properties for atom in origin.reagents] if origin.reagents else origin.properties,
        )
        self.name = origin.name
        self.tex = pygame.transform.scale(
            pygame.image.load(origin.tex_path).convert_alpha(), (SR / 8, SR / 8)
        )
        self.wpos = world_pos
        self.rect = self.tex.get_rect()
        self.reagents = origin.reagents

    def update(self, player, interactives):
        super().update(player, interactives)


class ArtifactType(Enum):
    "All possible types of artifacts"
    TONIC = 0
    KERNEL = 0
    DOCUMENT = 0


class Artifact:
    """ Base Artifact structure """

    def __init__(
        self,
        type_: ArtifactType,
        tex_path,
        name: str | None = None,
        reagents: List[Atom] | None = None,
        properties: List[Property] | None = None,
        color: pygame.Color | None = None,
    ):
        self.type = type_
        self.name = name
        self.tex_path = tex_path
        self.reagents = reagents
        self.properties = properties
        if color is not None:
            self.color = pygame.Color(color)
        else:
            self.color = color

        if not self.reagents:
            if not self.color:
                print(
                    f"Error: Initialized an Artifact with no reagents _and_ no color (by name of {name})"
                )
            if not self.properties:
                print(
                    f"Error: Initialized an Artifact with no reagents _and_ no properties (by name of {name})"
                )
                sys.exit(1)
        elif self.properties and self.color:
            print(
                "Error: Initialized an Artifact with no properties but also a given color"
            )
            sys.exit(1)

        # Blend the reagents' colors together to create backdrop
        if self.reagents:
            for atom in self.reagents:
                if self.color:
                    self.color = self.color.lerp(atom.color, 0.5)
                else:
                    self.color = pygame.Color(atom.color)  # the first iteration

        # _meth_ to determine whether text should be black or white
        luminance = (
            0.299 * self.color.r + 0.587 * self.color.g + 0.114 * self.color.b
        ) / 255
        self.text_color = Colors.BLACK if luminance > 0.5 else Colors.WHITE

    def to_world(self, world_pos):
        return ArtifactInteractive(self, world_pos)

    def to_hotbar(self):
        return ArtifactHotbar(self)


class ArtifactHotbar(Artifact):
    def __init__(self, origin: Artifact) -> None:
        super().__init__(
            origin.type,
            origin.name,
            origin.tex_path,
            origin.reagents,
            origin.properties,
            origin.color,
        )
        self.origin = origin
        self.image = pygame.Surface((38 * R, 38 * R))
        self.image.fill(self.color)
        write(
            self.image,
            "center",
            "".join([r.name for r in origin.reagents]) if self.reagents else self.name,
            fonts[24],
            self.text_color,
            *[s / 2 for s in self.image.size],
        )


class Artifacts:
    "All different artifact implementations"

    ARSENIC = Artifact(
        ArtifactType.TONIC,
        atom_sprs[0],
        "arsenic",
        reagents=[Atoms.ARSENIC],
    )

    TONIC_OF_LIFE = Artifact(
        ArtifactType.TONIC,
        Path("resources", "images", "artifacts", "tonic.png"),
        "Tonic of Life",
        properties=[
            Property(Properties.HEALTH, MagType.SET_COEF, 1.0),
            Property(Properties.MAX_HEALTH, MagType.SET_COEF, 1.5),
        ],
        color=Colors.GREEN,
    )

    KERNEL_OF_IDEOLOGY = Artifact(
        ArtifactType.KERNEL,
        Path("resources", "images", "artifacts", "kernel.png"),
        "Kernel of Ideology",
        properties=[
            Property(Properties.DODGE_CHANCE, MagType.REL_NUM, +0.1),
            Property(Properties.TRADE_FOR_CHOICES, MagType.SET_ABS, 2),
        ],
        color=Colors.GREEN,
    )
