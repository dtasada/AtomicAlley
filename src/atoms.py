from __future__ import absolute_import, annotations
from copy import deepcopy
from enum import Enum
from typing import List
from pathlib import Path

from .engine import *
from .objects import *
from .properties import *


class AtomTypes(Enum):
    ARSENIC = 0
    SILICON = 1
    OSMIUM = 2
    KRYPTON = 3
    VANADIUM = 4
    BISMUTH = 5
    OGANESSON = 6


atom_sprs = imgload("resources", "images", "atoms", "atoms.png", columns=7, frames=7)


class Atom:
    "Base Atom structure"

    def __init__(
        self,
        name: str,  #
        properties: List[Property],
        color: pygame.Color,
    ):
        self.name = name.capitalize()
        self.tex_path = Path("resources", "images", "atoms", "atoms.png")
        self.color = color
        self.properties = properties


class Atoms:
    "All different atom implementations"
    ARSENIC = Atom(
        "arsenic",
        [
            Property(Properties.DAMAGE, MagType.REL_COEF, +0.2),
            Property(Properties.MAX_HEALTH, MagType.REL_COEF, -0.2),
            Property(Properties.IGNITE_CHANCE, MagType.REL_COEF, +0.05),
        ],
        (163, 0, 0)
    )

    BISMUTH = Atom(
        "bismuth",
        [
            Property(Properties.MUT_ALL_STATS, MagType.REL_COEF, +0.1),
            Property(Properties.TRADE_FOR_CHOICES, MagType.SET_ABS, +2),
        ],
        (227, 171, 188)
    )

    KRYPTON = Atom(
        "krypton",
        [
            Property(Properties.DASH_COOLDOWN, MagType.REL_COEF, -0.5),
            Property(Properties.DASH_RANGE, MagType.REL_COEF, +1.0),
            # another one w/ a shield that kicks in at random times?
        ],
        (0, 0, 80)
    )

    OGANESSON = Atom(
       "oganesson",
        [Property(Properties.ULTIMATE, MagType.SET_ABS, 0.0)],
        (10, 10, 10)
        # TODO oganesson clor
    )

    OSMIUM = Atom(
        "osmium",
        [Property(Properties.NONE, MagType.SET_ABS, 0.0)],
        (50, 50, 50),
    )

    SILICON = Atom(
        "silicon",
        [
            Property(Properties.HEALTH_REGEN, MagType.REL_COEF, +0.5),
            Property(Properties.MOVEMENT_SPEED, MagType.REL_COEF, -0.2),
            Property(Properties.SIPHON, MagType.SET_ABS, 0.05),
        ],
        (254, 251, 234)
    )


    """
    ik doe de trial of silence 30 dagen (monk thing you wouldnt undersatnd)
    i shaved my head
    but 1 exception i dont have to be a virgin
    """

    VANADIUM = Atom(
        "vanadium",
        [
            Property(Properties.CRIT_CHANCE, MagType.REL_COEF, +0.5),
            Property(Properties.HOTBAR_SLOTS, MagType.REL_NUM, -1),
            Property(Properties.DODGE_CHANCE, MagType.SET_ABS, 0.1),
            Property(Properties.MOVEMENT_SPEED, MagType.REL_COEF, -0.2),
        ],
        (0, 200, 0)
    )
