from dataclasses import dataclass
from typing import Literal

from Magic.Ability import Ability

Color = Literal[
    "White",
    "Blue",
    "Black",
    "Red",
    "Green",
    "None",
]


@dataclass
class Card:
    id: str = ""
    name: str = ""
    type: str = ""
    color: list[Color] = None
    tapped: bool = False
    image: str = ""

    activated_ability: Ability = None

    def __eq__(self, value):
        return self.id == value.id

    def __hash__(self) -> int:
        return hash(self.id)

@dataclass
class Land(Card):
    mana_color: Color = "None"

    def __hash__(self) -> int:
        return super.__hash__(self)
    
@dataclass
class Spell(Card):
    cost: dict[Color, int] = None
    subtype: str = ""

    def __hash__(self):
        return super().__hash__(self)

@dataclass
class Creature(Spell):
    power: int = 0
    toughness: int = 0
    damage_counter: int = 0

    def __hash__(self) -> int:
        return super.__hash__(self)

@dataclass
class Sorcery(Spell):
    ...

@dataclass
class Instant(Spell):
    ...
