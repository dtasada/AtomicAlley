from .engine import *
from .objects import *

from copy import deepcopy
from enum import Enum
from typing import List
from pathlib import Path

import inspect


class Craftable(Enum):
    "Whether a given atom can be used to craft an artifact"
    KERNEL_OF_IDEOLOGY = 0


class Atoms:
    "All different atom implementations"

    @staticmethod
    def ARGON():
        return deepcopy(
            Atom(
                inspect.currentframe().f_code.co_name.capitalize(),  # dynamically set atom name to method name (e.g. def ARGON, so Atom.name = "Argon")
                Path("resources", "images", "atoms", "argon.jpg"),
                [Craftable.KERNEL_OF_IDEOLOGY],
            )
        )

    """
    @staticmethod
    def ARSENIC(): ...
    @staticmethod
    def BISMUTH(): ...
    @staticmethod
    def IODINE(): ...
    @staticmethod
    def KRYPTON(): ...
    @staticmethod
    def OGANESSON(): ...
    @staticmethod
    def OSMIUM(): ...
    @staticmethod
    def RHODIUM(): ...
    @staticmethod
    def SCANDIUM(): ...
    @staticmethod
    def SILICON(): ...
    @staticmethod
    def TUNGSTEN(): ...
    @staticmethod
    def VANADIUM(): ...
    """


class Atom:
    "Base Atom structure"

    def __init__(self, name, tex_path, properties: List[Craftable]):
        self.name = name
        self.tex_path = tex_path
        self.properties = properties
