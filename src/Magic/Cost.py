from dataclasses import dataclass
from typing import Any, Callable

from src.Magic.Literals import Color


def nothing_to_pay(*args) -> bool:
    return True

def pay_for_nothing(*args) -> None:
    return

@dataclass
class Cost:
    mana_cost: dict[Color, int]
    
    has_extra_cost: bool = False
    can_pay_extra_cost: Callable[[Any, Any, Any, list], bool] = None
    pay_extra_cost: Callable[[Any, Any, Any, list], None] = None
