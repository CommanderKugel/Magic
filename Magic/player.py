from dataclasses import dataclass

from Magic.Card import Card, Land, Creature
from Magic.Library import draw_card


class Player:
    def __init__(self, starting_life: int,  library: list[Card]):
        self.life = starting_life
        self.library: list[Card] = library
        self.graveyard: list[Card] = []

        self.hand: list[Card] = []
        self.creatures: list[Creature] = []
        self.lands: list[Land] = []

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
        """Play a land from hand.
        Raises Value error if Card not present in hand.
        """
        self.hand.remove(land)
        self.lands.append(land)
    
    def play_creature_from_hand(self, creature: Card) -> None:
        """Cast a creature from hand.
        Raises Value error if Card not present in hand.
        """
        self.hand.remove(creature)
        self.creatures.append(creature)
    
    def choose_action_dummy(
        self, 
        hit_landdrop: bool = False,
    ) -> Card | None:
        """
        Manually choose an action to make.
        Passes for all non sorcery speed actions.
        """
        for i, c in enumerate(self.hand):
            print(f"{i}: {c}")

        while True:
            i = input("\nChoose a card by index or 'p' for passing: ")
            if i.lower() == "p":
                return None
            if i not in "0123456789":
                print("Choose an integer, idiot.")
                continue
            if int(i) < 0 or int(i) >= len(self.hand):
                print("Index out of range, idiot.")
                continue
            card = self.hand[int(i)]
            if isinstance(card, Land) and hit_landdrop:
                print("You can only play one land a turn, idiot.")
                continue
            break
        return card
