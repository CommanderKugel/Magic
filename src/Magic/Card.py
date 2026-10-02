from dataclasses import dataclass
from typing import Literal, Callable

from src.Magic.Ability import Ability
from src.Magic.Literals import Color
from src.Magic.Buff import Buff


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
    subtype: str = ""

    summoning_sick: bool = True
    buffs: list[Buff] | None = None

    def get_power(self) -> int:
        """Fetch this creatures power."""
        if len(self.buffs) > 0:
            return self.base_power + sum(b.power for b in self.buffs)
        return self.base_power

    def get_toughness(self) -> int:
        """Fetch this creatures toughness."""
        if len(self.buffs) > 0:
            return self.base_toughness + sum(b.toughness for b in self.buffs)
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
