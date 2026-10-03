from dataclasses import dataclass
from typing import Literal, Callable

from src.Magic.Ability import Ability
from src.Magic.Literals import Color
from src.Magic.Modifier import Modifier


@dataclass
class Card:
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
    mana_color: Color = "None"

    def __hash__(self) -> int:
        return super.__hash__(self)
    
@dataclass
class Spell(Card):
    """Parent Class for Creature, Sorcery and Instant."""
    cost: dict[Color, int] = None
    sorcery_speed: bool = True
    targets: list[Card] | None = None

    def __hash__(self):
        return super().__hash__(self)

@dataclass
class Creature(Spell):
    base_power: int = 0
    base_toughness: int = 0
    damage_counter: int = 0
    subtype: list[str] | None = None

    summoning_sick: bool = True

    # Keywords
    flying: bool = False
    reach: bool = False
    trample: bool = False

    modifiers: list[Modifier] | None = None

    def get_power(self) -> int:
        """Fetch this creatures power."""
        if len(self.modifiers) > 0:
            return self.base_power + sum(b.get_power_mod() for b in self.modifiers)
        return self.base_power

    def get_toughness(self) -> int:
        """Fetch this creatures toughness."""
        if len(self.modifiers) > 0:
            return self.base_toughness + sum(b.get_toughness_mod() for b in self.modifiers)
        return self.base_toughness

    def __hash__(self) -> int:
        return super.__hash__(self)

@dataclass
class Sorcery(Spell):
    ability: Ability | None = None

@dataclass
class Instant(Spell):
    sorcery_speed: bool = False
    ability: Ability | None = None
