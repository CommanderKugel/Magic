from dataclasses import dataclass
from typing import Literal

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

@dataclass
class Land(Card):
    mana_color: Color = "None"
    
@dataclass
class Creature(Card):
    cost: dict[Color, int] = None
    subtype: str = ""
    power: int = 0
    toughness: int = 0


Forest = Land(
    name="Forest", 
    color=["None"], 
    type="Basic Land", 
    mana_color="G",
    tapped=False,
    image="Forest.png",
)

Bear = Creature(
    name="Bear",
    type="Creature",
    subtype="Beast",
    color=["G"],
    cost={"G": 2},
    power=2,
    toughness=2,
    tapped=False,
    image="Balduvian_Bears.png",
)
