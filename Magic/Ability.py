from dataclasses import dataclass
from typing import Callable

@dataclass
class Ability:
    is_mana_ability: bool = False

    can_activate: Callable | None = None
    pay_cost: Callable | None = None
    activity: Callable | None = None
