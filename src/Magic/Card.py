from dataclasses import dataclass
from typing import Literal, Callable

from src.Magic.Ability import Ability
from src.Magic.Literals import Color
from src.Magic.Modifier import Modifier, KeywordBuff


@dataclass
class Card:
    id: str = ""
    name: str = ""
    color: list[Color] = None
    tapped: bool = False

    activated_ability: Ability = None

    def __eq__(self, value):
        return self.id == value.id

    def __hash__(self) -> int:
        return hash(self.id)

    def reset(self) -> None:
        """Resets cards fields default values."""
        self.tapped = False

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

    def __hash__(self):
        return super().__hash__(self)

    def reset(self):
        """Resets cards fields default values."""
        self.tapped = False
        self.targets = None

@dataclass
class Creature(Spell):
    base_power: int = 0
    base_toughness: int = 0
    damage_counter: int = 0
    subtype: list[str] | None = None

    summoning_sick: bool = True

    # Keywords
    _flying: bool = False
    _reach: bool = False
    _trample: bool = False

    modifiers: list[Modifier] | None = None

    def reset(self) -> None:
        """Resets cards fields default values."""
        self.tapped = False
        self.targets = None
        self.damage_counter = 0
        self.summoning_sick = True

        # remove self from modifiers
        for mod in self.modifiers:
            if isinstance(mod.target, Creature):
                mod.target = None
            if isinstance(mod.target, list):
                if self in mod.target:
                    mod.target.remove(self)

        # remove modifiers from self        
        self.modifiers = []

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

    def has_trample(self) -> bool:
        """Returns True if this creature has Trample, False if not."""
        return (
            self._trample 
            or any(x for x in self.modifiers if isinstance(x, KeywordBuff) and x.trample)
        )

    def is_flying(self) -> bool:
        """Returns True if this creature is flying, False if not."""
        return (
            self._flying 
            or any(x for x in self.modifiers if isinstance(x, KeywordBuff) and x.flying)
        )

    def has_reach(self) -> bool:
        """Returns True if this creature has reach, False if not."""
        return (
            self._reach 
            or any(x for x in self.modifiers if isinstance(x, KeywordBuff) and x.reach)
        )

    def __hash__(self) -> int:
        return super.__hash__(self)

@dataclass
class Sorcery(Spell):
    ability: Ability | None = None

@dataclass
class Instant(Spell):
    sorcery_speed: bool = False
    ability: Ability | None = None
