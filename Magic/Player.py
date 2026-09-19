import random
from typing import Literal, Any

from Magic.Card import Card, Land, Creature, Color
from Magic.Library import draw_card

Action = Literal[
    "Pass",
    "Play",
    "Cast",
    "Ability",
]

PASS: tuple[Action, None] = ("Pass", None)


def _is_valid_action(i: str, max_idx: int) -> bool:
    """Verify the input string maps to a valid action"""
    if i.strip() == "":
        print("Empty string is not an integer, idiot.")
        return False
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

    def discard(self, card: Card | None) -> None:
        """Discard a card to graveyard. Choose a random one if no card is provided."""
        if card is not None:
            card = random.choice(self.hand)
        self.graveyard.append(card)
        self.hand.remove(card)
        
    
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
        self.lands.append(land)
        self.hand.remove(land)

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

    
    def play_creature_from_hand(self, creature: Card) -> None:
        """Cast a creature from hand. Raises Value error if Card not present in hand."""
        if self.pay_for_manacost(creature):
            print("Successfully payed the creatures Manacost.")
            self.hand.remove(creature)
            self.creatures.append(creature)
        else:
            print("Did not succeed on paying the creatures Manacost.")

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
        """Manually choose an action to make. Passes for all non sorcery speed actions.
        Returns (ActionType, Card | None)
        """
        actions = (
            [
                (
                    "Play" if isinstance(card, Land) else "Cast",
                    card
                ) 
                for card in self.hand
                if not isinstance(card, Land) or not hit_landdrop
            ] + [
                ("Ability", x)
                for x in self.lands + self.creatures + self.hand
                if x.activated_ability is not None
                and x.activated_ability.can_activate(x, self)
            ] + [
                PASS
            ]
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
    