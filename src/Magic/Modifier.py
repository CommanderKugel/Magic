from dataclasses import dataclass
from typing import Any

@dataclass
class Modifier:
    target: Any | None = None
    
    def get_power_mod(self) -> int:
        return 0

    def get_toughness_mod(self) -> int:
        return 0

@dataclass
class Buff(Modifier):
    power: int = 0
    toughness: int = 0

    def get_power_mod(self) -> int:
        return self.power
    
    def get_toughness_mod(self) -> int:
        return self.toughness

@dataclass
class KeywordBuff(Modifier):
    flying: bool = False
    trample: bool = False
    reach: bool = False
