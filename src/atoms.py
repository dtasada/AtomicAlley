from __future__ import absolute_import, annotations
from enum import Enum
from typing import List

from .engine import *
from .objects import *
from .properties import *


class AtomTypes(Enum):
    # ARGON = 0
    ARSENIC = 0
    SILICON = 1
    OSMIUM = 2
    KRYPTON = 3
    VANADIUM = 4
    BISMUTH = 5
    OGANESSON = 6


atom_images: List[pygame.Surface] = imgload(
    "resources", "images", "atoms", "atoms.png", columns=7
)


class Atom:
    "Base Atom structure"

    def __init__(
        self,
        type_: AtomTypes,
        properties: List[Property],
        color: pygame.Color,
    ):
        self.name = type_.name.capitalize()
        self.image = atom_images[type_.value]
        self.color = color
        self.properties = properties


class Atoms:
    "All different atom implementations"
    # ARGON = Atom(
    #     AtomTypes.OSMIUM,
    #     [Property(Properties.NONE, MagType.SET_ABS, 0.0)],
    #     (50, 50, 50),
    # )

    ARSENIC = Atom(
        AtomTypes.ARSENIC,
        [
            Property(Properties.DAMAGE, MagType.REL_COEF, +0.2),
            Property(Properties.MAX_HEALTH, MagType.REL_COEF, -0.2),
        ],
        (163, 0, 0),
    )

    BISMUTH = Atom(
        AtomTypes.BISMUTH,
        [
        ],
        (227, 171, 188),
    )

    KRYPTON = Atom(
        AtomTypes.KRYPTON,
        [
            Property(Properties.DASH_COOLDOWN, MagType.REL_COEF, -0.5),
            Property(Properties.DASH_RANGE, MagType.REL_COEF, +1.0),
            # another one w/ a shield that kicks in at random times?
        ],
        (0, 0, 80),
    )

    # OGANESSON = Atom(
    #     AtomTypes.OGANESSON,
    #     [

    #     ],
    #     (10, 10, 10),
    #     # TODO oganesson clor
    # )

    OSMIUM = Atom(
        AtomTypes.OSMIUM,
        [Property(Properties.NONE, MagType.SET_ABS, 0.0)],
        (50, 50, 50),
    )

    SILICON = Atom(
        AtomTypes.SILICON,
        [
            Property(Properties.MOVEMENT_SPEED, MagType.REL_COEF, -0.2),
            Property(Properties.MAX_HEALTH, MagType.REL_COEF, +0.2)
        ],
        (254, 251, 234),
    )

    VANADIUM = Atom(
        AtomTypes.VANADIUM,
        [
            Property(Properties.CRIT_CHANCE, MagType.REL_COEF, +0.5),
            Property(Properties.MOVEMENT_SPEED, MagType.REL_COEF, -0.2),
        ],
        (0, 200, 0),
    )
