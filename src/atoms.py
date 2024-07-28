from __future__ import absolute_import, annotations
from copy import deepcopy
from enum import Enum
from typing import List
from pathlib import Path

from .engine import *
from .objects import *
from .properties import *

import inspect


class Atoms:
    "All different atom implementations"

    @staticmethod
    def ARSENIC():
        return deepcopy(
            Atom(
                inspect.currentframe().f_code.co_name,
                [
                    Property(Properties.DAMAGE, MagType.REL_COEF, +0.2),
                    Property(Properties.MAX_HEALTH, MagType.REL_COEF, -0.2),
                    Property(Properties.IGNITE_CHANCE, MagType.SET_ABS, 0.2),
                ],
            )
        )

    @staticmethod
    def BISMUTH():
        return deepcopy(
            Atom(
                inspect.currentframe().f_code.co_name,
                [
                    Property(Properties.MUT_ALL_STATS, MagType.REL_COEF, +0.1),
                    Property(Properties.TRADE_FOR_CHOICES, MagType.SET_ABS, +2),
                ],
            )
        )

    @staticmethod
    def KRYPTON():
        return deepcopy(
            Atom(
                inspect.currentframe().f_code.co_name,
                [
                    Property(Properties.DASH_COOLDOWN, MagType.REL_COEF, -0.5),
                    Property(Properties.DASH_RANGE, MagType.REL_COEF, +1.0),
                    # another one w/ a shield that kicks in at random times?
                ],
            )
        )

    @staticmethod
    def OGANESSON():
        return deepcopy(
            Atom(
                inspect.currentframe().f_code.co_name,
                [Property(Properties.ULTIMATE, MagType.SET_ABS, 0.0)],
            )
        )

    @staticmethod
    def OSMIUM():
        return deepcopy(
            Atom(
                inspect.currentframe().f_code.co_name,
                [Property(Properties.NONE, MagType.SET_ABS, 0.0)],
            )
        )

    @staticmethod
    def SILICON():
        return deepcopy(
            Atom(
                inspect.currentframe().f_code.co_name,
                [
                    Property(Properties.HEALTH_REGEN, MagType.REL_COEF, +0.5),
                    Property(Properties.MOVEMENT_SPEED, MagType.REL_COEF, -0.2),
                    Property(Properties.SIPHON, MagType.SET_ABS, 0.05),
                ],
            )
        )

    @staticmethod
    def VANADIUM():
        return deepcopy(
            Atom(
                inspect.currentframe().f_code.co_name,
                [
                    Property(Properties.CRIT_CHANCE, MagType.REL_COEF, +0.5),
                    Property(Properties.HOTBAR_SLOTS, MagType.REL_NUM, -1),
                    Property(Properties.DODGE_CHANCE, MagType.SET_ABS, 0.1),
                    Property(Properties.MOVEMENT_SPEED, MagType.REL_COEF, -0.2),
                ],
            )
        )


class Atom:
    "Base Atom structure"

    def __init__(
        self,
        name: str,  #
        properties: List[Property],
        color: pygame.Color,
    ):
        self.name = name.capitalize()
        self.tex_path = Path("resources", "images", "atoms", f"{name.lower()}.png")
        self.color = color
        self.properties = properties
