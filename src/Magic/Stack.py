from dataclasses import dataclass
from typing import Callable

from src.Magic.Card import Card
from src.Magic.Literals import Action, PriorityState
from src.Player.Player import Player


@dataclass
class StackObject:
    action: Action
    source: Card
    owner: Player
    targets: list[Card | Player] | None = None

@dataclass
class PriorityData:
    state: PriorityState
    priority_player: Player
    non_priority_player: Player
    pass_counter: int = 0

    def swap_priority(self) -> None:
        """Swap values of priority_player and non_priority_player."""
        self.priority_player, self.non_priority_player = self.non_priority_player, self.priority_player
        