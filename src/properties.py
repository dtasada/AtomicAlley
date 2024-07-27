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
    DODGE_CHANCE = 5
    HEALTH_REGEN = 6
    HEALTH = 7
    HOTBAR_SLOTS = 8
    IGNITE_CHANCE = 9
    MAX_HEALTH = 10
    MOVEMENT_SPEED = 11
    MUT_ALL_STATS = 12
    NONE = 13  # Osmium is ass and it doesn't do anything. It's the unlucky atom
    SHIELD = 14
    SIPHON = 15
    TRADE_FOR_CHOICES = 16
    ULTIMATE = 17


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
