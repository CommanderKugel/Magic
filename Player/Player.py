import random
import uuid
from typing import Literal, Any

from Magic.Card import Card, Spell, Land, Creature, Color
from Magic.Library import draw_card
from Magic.Literals import Action
from Magic.Ability import Ability


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
    def __init__(self, name: str, starting_life: int,  library: list[Card]):
        self.name: str = name

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
                raise Exception(f"not {self.name}")
            self.hand.append(c)

    def discard(self, card: Card | None) -> None:
        """Discard a card to graveyard. Choose a random one if no card is provided."""
        if card is not None:
            card = random.choice(self.hand)
        self.graveyard.append(card)
        self.hand.remove(card)
        
    def clear_floating_mana(self) -> None:
        """Set all floating mana to zero."""
        self.floating_mana = {
            "White": 0,
            "Blue": 0,
            "Black": 0,
            "Red": 0,
            "Green": 0,
            "None": 0,
        }

    def pay_for_manacost(self, card: Creature, opponent) -> bool:
        """
        Tries to pay for manacost. 
        Returns True if cost was payed, False if not.
        Mana can be lost if the payment was messed up.
        Randomly activates mana abilities to pay, if not enough floating mana is available.
        Only supports moncolored spells for now.
        """
        assert (
            len(card.cost) == 1
            or len(card.cost) == 2 and "None" in card.cost.keys()
        )
        color = list(card.cost.keys())[0]
        assert color != "None"

        # 1. determine mana cost
        colored_cost = card.cost.get(color, 0)
        generic_cost = card.cost.get("None", 0)

        # 2. determine available mana
        mana_abilities: list[Ability, Card, Color] = self.collect_mana_abilities()
        colored_available = self.floating_mana.get(color, 0) + sum(
            1 
            for _, card, _ 
            in mana_abilities if card.activated_ability.mana_color == color
        )
        generic_available = sum(self.floating_mana.values()) + len(mana_abilities) - colored_cost

        # 3. return False if not enough mana is available
        if colored_cost > colored_available or generic_cost > generic_available:
            return False

        # 4. pay using floating mana
        used = min(self.floating_mana[color], colored_cost)
        self.floating_mana[color] -= used
        colored_cost -= used

        used = min(self.floating_mana["None"], generic_cost)
        self.floating_mana["None"] -= used
        generic_cost -= used

        # 5. pay using mana abilities
        random.shuffle(mana_abilities)
        for _, card, _ in mana_abilities:
            if colored_cost == 0 and generic_cost == 0:
                return True

            color_needed = card.activated_ability.mana_color == color and colored_cost > 0
            generic_needed = generic_cost > 0

            # only activate abilities that are useful to us
            if color_needed or generic_needed:
                card.activated_ability.pay_cost(card, self, opponent)
                card.activated_ability.activity(card, self, opponent)

                if color_needed:
                    self.floating_mana[color] -= 1
                    colored_cost -= 1
                elif generic_needed:
                    self.floating_mana[color] -= 1
                    generic_cost -= 1
        
        return generic_cost == 0 and colored_cost == 0

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

    def choose_action(self, sorcery_speed: bool, hit_landdrop: bool, opponent) -> tuple[Action, Card | None]:
        """To be implemented by child class."""
        raise NotImplementedError()

    def binary_choice(self, question: str) -> bool:
        """To be implemented by child class."""
        raise NotImplementedError()

    def distribute_damage_to_blocker(self, attacker: Creature, blocker: list[Creature]) -> dict[Card, int]:
        """To be implemented by child class."""
        raise NotImplementedError()

    def collect_actions(self, sorcery_speed: bool, hit_landdrop: bool, opponent) -> list[tuple[Action, Card]]:
        """Generate a list of all legal non-mana-ability actions."""
        actions = []
        # cast spells
        actions.extend([
            ("Cast", card)
            for card in self.hand
            if isinstance(card, Spell) 
            and (sorcery_speed or not card.sorcery_speed)
        ])
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
            and not card.activated_ability.is_mana_ability
            and card.activated_ability.can_activate(card, self, opponent)
        ] 
        # passing
        actions.append(PASS)
        return actions

    def collect_mana_abilities(self) -> list[tuple[Action, Card, Color]]:
        """Generate a list of all mana-ability actions."""
        actions = [
            ("Ability", card, card.activated_ability)
            for card in self.lands + self.creatures + self.hand
            if card.activated_ability is not None
            and card.activated_ability.is_mana_ability
            and card.activated_ability.can_activate(card, self, None)
        ]
        return actions
    