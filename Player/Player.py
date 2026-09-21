import random
import uuid
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
        self.name: str

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

    def pay_for_manacost(self, card: Creature) -> bool:
        """To be implemented by child class."""
        raise NotImplementedError()

    
    def play_creature_from_hand(self, creature: Card) -> None:
        """Cast a creature from hand. Raises Value error if Card not present in hand."""
        if self.pay_for_manacost(creature):
            print("Successfully payed the creatures Manacost.")
            self.hand.remove(creature)
            self.creatures.append(creature)
        else:
            print("Did not succeed on paying the creatures Manacost.")

    def play_land_from_hand(self, land: Land) -> None:
        """Play a land from hand. Raises Value error if Card not present in hand."""
        self.lands.append(land)
        self.hand.remove(land)

    def target(
        self, 
        opp = None, # Player
        own_player: bool = False,
        own_creatures: bool = False, 
        own_hand: bool = False,
        opp_player: bool = False,
        opp_creatures: bool = False,
    ) -> Card | Any:
        """To be implemented by child class."""
        raise NotImplementedError()

    def choose_action_dummy(self, sorcery_speed: bool, hit_landdrop: bool) -> tuple[Action, Card | None]:
        """To be implemented by child class."""
        raise NotImplementedError()

    def binary_choice(self, question: str) -> bool:
        """To be implemented by child class."""
        raise NotImplementedError()

    def collect_actions(self, sorcery_speed: bool, hit_landdrop: bool) -> list[tuple[Action, Card]]:
        """Generate a list of all pseudo-legal actions."""
        actions = []
        # cast spells
        if sorcery_speed:
            actions += [
                ("Cast", card)
                for card in self.hand
                if not isinstance(card, Land)
            ]
        # play lands
        if sorcery_speed and not hit_landdrop:
            actions += [
                ("Play", card)
                for card in self.hand
                if isinstance(card, Land)
            ]
        # activated abilities
        actions += [
            ("Ability", card)
            for card in self.lands + self.creatures + self.hand
            if card.activated_ability is not None
            and card.activated_ability.can_activate(card, self)
        ] 
        # passing
        actions.append(PASS)
        return actions
    