from .engine import *


class MagType(Enum):
    SET_ABS = 0  # Set property to magnitude, where magnitude is an absolute number
    REL_NUM = 1  # Add or remove magnitude from property, where magnitude is an absolute number
    REL_COEF = 2  # Add/remove magnitude from property, where magnitude is a coefficient
    SET_COEF = 3  # Set property to magnitude, where magnitude is a coefficient


class Properties(Enum):
    CRIT_CHANCE = 0
    DAMAGE = 1
    DASH_COOLDOWN = 2
    DASH_DAMAGE = 3
    DASH_RANGE = 4
    MAX_HEALTH = 5
    MOVEMENT_SPEED = 6
    NONE = 7


class Property:
    def __init__(
        self,
        type_: Properties,
        mag_type: MagType,
        magnitude: float,
    ) -> None:
        self.type = type_
        self.mag_type = mag_type
        self.magnitude = magnitude
