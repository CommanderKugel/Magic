from typing import Literal

from Magic.Card import Card, Land, Creature, Color
from Magic.Library import draw_card

Action = Literal[
    "Pass",
    "Play",
    "Cast",
    "Ability",
]

PASS: tuple[Action, None] = ("Pass", None)


class Player:
    def __init__(self, starting_life: int,  library: list[Card]):
        self.life = starting_life
        self.library: list[Card] = library
        self.graveyard: list[Card] = []

        self.hand: list[Card] = []
        self.creatures: list[Creature] = []
        self.lands: list[Land] = []

        self.floating_mana: dict[Color, int] = {
            "White": 0,
            "Blue": 0,
            "Black": 0,
            "Red": 0,
            "Green": 0,
            "None": 0,
        }

    def draw(self, n: int) -> None:
        """Draw n cards and add them to the hand."""
        for _ in range(n):
            c = draw_card(self.library)
            if c is None:
                print("LOL decked out!")
                return
            self.hand.append(c)
    
    def clear_floating_mana(self) -> None:
        """Sets all floating mana to zero."""
        self.floating_mana = {
            "White": 0,
            "Blue": 0,
            "Black": 0,
            "Red": 0,
            "Green": 0,
            "None": 0,
        }

    def play_land_from_hand(self, land: Card) -> None:
        """Play a land from hand. Raises Value error if Card not present in hand."""
        self.hand.remove(land)
        self.lands.append(land)
    
    def play_creature_from_hand(self, creature: Card) -> None:
        """Cast a creature from hand. Raises Value error if Card not present in hand."""
        self.hand.remove(creature)
        self.creatures.append(creature)
    
    def choose_action_dummy(self, hit_landdrop: bool) -> tuple[Action, Card | None]:
        """Manually choose an action to make. Passes for all non sorcery speed actions.
        Returns (ActionType, Card | None)
        """

        def is_valid_action(i: str, max_idx: int) -> bool:
            """Verify the input string maps to a valid action"""
            # not a number
            for c in i:
                if c not in "0123456789":
                    print("Choose an integer, idiot.")
                    return False
            # out of bounds
            if int(i) < 0 or int(i) >= max_idx:
                print("Index out of range, idiot.")
                return False
            # all okay
            return True

        # collect all actions
        actions = (
            [
                (
                    "Play" if isinstance(c, Land) else "Cast",
                    c
                ) 
                for c in self.hand
                if not isinstance(c, Land) or not hit_landdrop
            ] + [
                ("Ability", x)
                for x in self.lands + self.creatures + self.hand
                if x.activated_ability is not None
                and x.activated_ability.can_activate(x)
            ] + [
                PASS
            ]
        )

        # human chooses from actions
        for i, (act, card) in enumerate(actions):
            print(f"{i}: {act}; {card}")
        i = input("\nChoose an action by index: ")

        # action legality
        if not is_valid_action(i, len(actions)):
            print("Invalid action, returning PASS")
            return PASS

        # return chosen action
        return actions[int(i)]
