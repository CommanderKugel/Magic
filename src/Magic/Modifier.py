from dataclasses import dataclass
from typing import Any

@dataclass(eq=False)
class Modifier:
    target: list[Any] | None = None
    
    def get_power_mod(self) -> int:
        return 0

    def get_toughness_mod(self) -> int:
        return 0

@dataclass(eq=False)
class Buff(Modifier):
    power: int = 0
    toughness: int = 0

    def get_power_mod(self) -> int:
        return self.power
    
    def get_toughness_mod(self) -> int:
        return self.toughness

@dataclass(eq=False)
class KeywordBuff(Modifier):
    flying: bool = False
    trample: bool = False
    reach: bool = False
