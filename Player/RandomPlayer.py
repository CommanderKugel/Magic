import random
from typing import Any

from Magic.Card import Card, Creature, Land
from Magic.Ability import Ability
from Player.Player import Player, Action, Color


class RandomPlayer(Player):
    def __init__(self, name, starting_life, library):
        super().__init__(name, starting_life, library)

    def target(
        self, 
        opp = None,
        own_player: bool = False,
        own_creatures: bool = False, 
        own_hand: bool = False,
        opp_player: bool = False,
        opp_creatures: bool = False,
    ) -> Card | Any:
        """Choose a valid target at random."""
        targets: list[tuple[str, Card]] = []
        if own_player:
            targets.append(("OwnPlayer", self))
        if own_creatures:
            for creature in self.creatures:
                targets.append(("OwnCreature", creature))
        if own_hand:
            for card in self.hand:
                targets.append(("OwnHand", card))
        if opp_player:
            targets.append(("OppPlayer", opp))
        if opp_creatures:
            for creature in opp.creatures:
                targets.append(("OppCreature", creature))

        return random.choice(targets)

    def distribute_damage_to_blocker(self, attacker, blocker) -> dict[Creature, int]:
        """Distribute the damage across the blockers."""
        remaining_power = attacker.power
        random.shuffle(blocker)
        result = {}
        for block in blocker:
            if block.toughness <= remaining_power:
                result[block] = block.toughness
                remaining_power -= block.toughness
            else:
                result[block] = 0
        return result

    def choose_action(self, sorcery_speed: bool, hit_landdrop: bool, opponent) -> tuple[Action, Card | None]:
        """Choose an action at random. Returns (ActionType, Card | None)"""
        actions = self.collect_actions(
            sorcery_speed=sorcery_speed, 
            hit_landdrop=hit_landdrop,
            opponent=opponent,
        )
        return random.choice(actions)

    def binary_choice(self, question: str) -> bool:
        """Decide binary choice at random."""
        return bool(random.getrandbits(1))
