from dataclasses import dataclass
from typing import Any

@dataclass
class Buff:
    target: Any | None = None
    power: int = 0
    toughness: int = 0
