from dataclasses import dataclass
from typing import Callable, Any

from src.Magic.Literals import Color

@dataclass(eq=False)
class Ability:
    is_mana_ability: bool = False
    mana_color: Color | None = None

    mana_cost: dict[Color, int] | None = None

    can_activate: Callable[[Any, Any, Any], bool] = None
    choose_targets: Callable[[Any, Any, Any], list[Any]] = None
    pay_cost: Callable[[Any, Any, Any, list], None] = None
    activity: Callable[[Any, Any, Any, list], None] = None
