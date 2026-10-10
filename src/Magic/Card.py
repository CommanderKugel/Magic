from dataclasses import dataclass
from typing import Literal, Callable

from src.Magic.Ability import Ability, TriggeredAbility
from src.Magic.Literals import Color
from src.Magic.Modifier import Modifier, KeywordBuff
from src.Magic.Cost import Cost


@dataclass(eq=False)
class Card:
    id: str = ""
    name: str = ""
    color: list[Color] = None
    tapped: bool = False

    activated_ability: Ability = None
    etb_ability: Ability = None
    triggered_ability: TriggeredAbility = None

    def __eq__(self, value):
        return self.id == value.id

    def __hash__(self) -> int:
        return hash(self.id)

    def reset(self) -> None:
        """Resets cards fields default values."""
        self.tapped = False

@dataclass(eq=False)
class Land(Card):
    mana_color: Color = "None"

    def __hash__(self) -> int:
        return super.__hash__(self)
    
@dataclass(eq=False)
class Spell(Card):
    """Parent Class for Creature, Sorcery and Instant."""
    cost: Cost = None
    sorcery_speed: bool = True

    def __hash__(self):
        return super().__hash__(self)

    def reset(self):
        """Resets cards fields default values."""
        self.tapped = False
        self.targets = None

@dataclass(eq=False)
class Artifact(Spell):
    subtype: list[str] | None = None

@dataclass(eq=False)
class Creature(Spell):
    base_power: int = 0
    base_toughness: int = 0
    damage_counter: int = 0
    subtype: list[str] | None = None

    summoning_sick: bool = True

    def not_summoning_sick(self) -> bool:
        """Returns True if the creature is summoning sick, False if not."""
        return not self.summoning_sick or self.has_haste()

    # Keywords
    _flying: bool = False
    _reach: bool = False
    _trample: bool = False
    _haste: bool = False

    modifiers: list[Modifier] | None = None

    def reset(self) -> None:
        """Resets cards fields default values."""
        self.tapped = False
        self.targets = None
        self.damage_counter = 0
        self.summoning_sick = True

        # remove self from modifiers
        for mod in self.modifiers[:]:
            self.disconnect_modifier(mod)

    def connect_modifier(self, mod: Modifier) -> None:
        """Set references both ways."""
        self.modifiers.append(mod)
        mod.target.append(self)

    def disconnect_modifier(self, mod: Modifier) -> None:
        """Remove references both ways."""
        self.modifiers.remove(mod)
        mod.target.remove(self)

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
    
    def has_haste(self) -> bool:
        """Returns True if this creature has haste, False if not."""
        return (
            self._haste
            or any(x for x in self.modifiers if isinstance(x, KeywordBuff) and x.haste)
        )

    def __hash__(self) -> int:
        return super.__hash__(self)

@dataclass(eq=False)
class Sorcery(Spell):
    ability: Ability | None = None

@dataclass(eq=False)
class Instant(Spell):
    sorcery_speed: bool = False
    ability: Ability | None = None
