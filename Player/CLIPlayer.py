import random
from typing import Any

from Magic.Card import Card, Creature, Land
from Player.Player import (
    Player,
    _is_valid_action,
    Action,
    PASS,
)


class CLIPlayer(Player):
    def __init__(self, starting_life, library):
        super().__init__(starting_life, library)

    def pay_for_manacost(self, card: Creature) -> bool:
        """Return True if the cost was payed successfully. False if not."""
        # check total mana
        if sum(self.floating_mana.values()) < sum(card.cost.values()):
            print("Not enough floating mana to cast this spell.")
            return False
        relevant_colors = [
            c
            for c in ["White", "Blue", "Black", "Red", "Green"]
            if c in card.cost.keys()
        ]
        # check pips
        if any(
            self.floating_mana[c] < card.cost[c]
            for c in relevant_colors
        ):
            print("not enough pips in floating mana to cast this spell.")
            return False
        # pay for colored mana now
        for c in relevant_colors:
            self.floating_mana[c] -= card.cost[c]
        # pay for colorless mana using colorless floating mana
        if "None" in card.cost:
            if self.floating_mana["None"] >= card.cost["None"]:
                self.floating_mana["None"] -= card.cost["None"]
                return True
            # pay for remaining colorless cost using floating colored mana
            remaining = card.cost["None"] - self.floating_mana["None"]
            self.floating_mana["None"] = 0
            while remaining > 0:
                c = random.choice([
                    c for c in self.floating_mana.keys()
                    if self.floating_mana[c] > 0
                ])
                self.floating_mana[c] -= 1
                remaining -= 1
        return True

    def target(
        self, 
        opp = None,
        own_player: bool = False,
        own_creatures: bool = False, 
        own_hand: bool = False,
        opp_player: bool = False,
        opp_creatures: bool = False,
    ) -> Card | Any:
        """Choose a specific target."""
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
            targets.append(opp)
        if opp_creatures:
            for creature in opp.creatures:
                targets.append(("OppCreature", creature))
        
        for idx, (s, c) in enumerate(targets):
            print(f"{idx}: {s} - {c.name if isinstance(c, Card) else ""}")
        print()

        i = input("Choose an action: ")        
        if not _is_valid_action(i, len(targets)):
            i = random.randint(0, len(targets) - 1)
        target = targets[int(i)][1]
        print(f"Target: {target.name if isinstance(target, Card) else "Player"}")
        return target

    def choose_action_dummy(self, hit_landdrop: bool) -> tuple[Action, Card | None]:
        """Manually choose an action to make. Returns (ActionType, Card | None)"""
        actions = self.collect_actions(
            sorcery_speed=True,
            hit_landdrop=hit_landdrop,
        )
        # human chooses from actions
        for i, (act, card) in enumerate(actions):
            print(f"{i}: {act}; {card.name if card else ""}")
        i = input("\nChoose an action by index: ")
        # action legality
        if not _is_valid_action(i, len(actions)):
            print("Invalid action, returning PASS")
            return PASS
        # return chosen action
        return actions[int(i)]

    def binary_choice(self, question: str) -> bool:
        """Choice if player wants to accack with the given creature."""
        return (
            input(f"{question}\ny/n: ")
            .lower()
            .strip()
        ) == "y"
