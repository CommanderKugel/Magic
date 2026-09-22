from dataclasses import dataclass
from typing import Callable

from Magic.Literals import Color

@dataclass
class Ability:
    is_mana_ability: bool = False
    mana_color: Color | None = None

    can_activate: Callable | None = None
    pay_cost: Callable | None = None
    activity: Callable | None = None
