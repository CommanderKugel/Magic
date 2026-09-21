from dataclasses import dataclass
from typing import Literal, Callable

from Magic.Ability import Ability

Color = Literal[
    "White",
    "Blue",
    "Black",
    "Red",
    "Green",
    "None",
]

CardType = Literal[
    "Basic Land",
    "Creature",
    "Sorcery",
    "Instant",
]


@dataclass
class Card:
    type: CardType
    id: str = ""
    name: str = ""
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
    type: CardType = "Basic Land"
    mana_color: Color = "None"

    def __hash__(self) -> int:
        return super.__hash__(self)
    
@dataclass
class Spell(Card):
    """Parent Class for Creature, Sorcery and Instant."""
    cost: dict[Color, int] = None

    def __hash__(self):
        return super().__hash__(self)

@dataclass
class Creature(Spell):
    power: int = 0
    toughness: int = 0
    damage_counter: int = 0
    subtype: str = ""
    type: CardType = "Creature"

    def __hash__(self) -> int:
        return super.__hash__(self)

@dataclass
class Sorcery(Spell):
    ability: Ability | None = None
    type: CardType = "Sorcery"

@dataclass
class Instant(Spell):
    ability: Ability | None = None
    type: CardType = "Instant"
