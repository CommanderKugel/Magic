from dataclasses import dataclass
from typing import Callable

from Magic.Card import Card
from Player.Player import Player, Action

@dataclass
class StackObject:
    action: Action
    source: Card
    owner: Player
