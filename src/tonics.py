import json
from pprint import pprint
from .engine import *


with open("src/upgrades.json") as f:
    upgrade_data = json.load(f)


class Tonic:
    def __init__(self, *elems):
        self.elems = elems
        self.image = pygame.Surface((38 * R, 38 * R))
        self.data = upgrade_data[self.elems[0]]
        self.color, self.tcolor = self.data["color"], self.data["tcolor"]
        self.image.fill(self.color)
        write(self.image, "center", "".join(elems), fonts[24], self.tcolor, *[s / 2 for s in self.image.size])
        self.positives = []
        self.negatives = []
        for k, v in self.data.items():
            if k in ("color", "tcolor"):
                continue
            if v.startswith("+"):
                self.positives.append(f"{v} {k.replace('_', ' ')}")
            elif v.startswith("-"):
                self.negatives.append(f"{v} {k.replace('_', ' ')}")
            elif v.startswith("~"):
                self.positives.append(v)
