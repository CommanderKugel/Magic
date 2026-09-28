from dataclasses import dataclass
from typing import Callable, Any

from src.Magic.Literals import Color

@dataclass
class Ability:
    is_mana_ability: bool = False
    mana_color: Color | None = None

    _can_activate: Callable[[Any, Any, Any], bool] | None = None
    _choose_targets: Callable[[Any, Any, Any], bool] | None = None
    _pay_cost: Callable[[Any, Any, Any], bool] | None = None
    _activity: Callable[[Any, Any, Any], bool] | None = None

    def can_activate(self, source, owner, opponent):
        return self._can_activate(source, owner, opponent)

    def choose_targets(self, source, owner, opponent):
        return self._choose_targets(source, owner, opponent)

    def pay_cost(self, source, owner, opponent):
        return self._pay_cost(source, owner, opponent)

    def activity(self, source, owner, opponent):
        return self._activity(source, owner, opponent)
