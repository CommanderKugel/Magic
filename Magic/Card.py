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
    name: str = ""
    type: str = ""
    color: list[Color] = None
    tapped: bool = False
    image: str = ""

    activated_ability: Ability = None

@dataclass
class Land(Card):
    mana_color: Color = "None"
    
@dataclass
class Creature(Card):
    cost: dict[Color, int] = None
    subtype: str = ""
    power: int = 0
    toughness: int = 0
