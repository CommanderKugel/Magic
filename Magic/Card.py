from dataclasses import dataclass
from typing import Literal, Callable

from Magic.Ability import Ability
from Magic.Literals import CardType, Color


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
    sorcery_speed: bool = True

    def __hash__(self):
        return super().__hash__(self)

@dataclass
class Creature(Spell):
    type: CardType = "Creature"
    power: int = 0
    toughness: int = 0
    damage_counter: int = 0
    subtype: str = ""

    def __hash__(self) -> int:
        return super.__hash__(self)

@dataclass
class Sorcery(Spell):
    type: CardType = "Sorcery"
    targets: list[Card] | None = None
    ability: Ability | None = None

@dataclass
class Instant(Spell):
    type: CardType = "Instant"
    sorcery_speed = False
    ability: Ability | None = None
