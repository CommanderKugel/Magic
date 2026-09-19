from Magic.Ability import Ability
from Magic.Card import Card
from Magic.Player import Player


def is_not_tapped(source: Card, owner: Player) -> bool:
    """Return True if the card is untapped, and False if it is."""
    return not source.tapped

def tap_card(source: Card, owner: Player) -> None:
    """Tap the card."""
    source.tapped = True

def add_g_mana(source: Card, owner: Player) -> None:
    """Adds one Green Mana to the players Manapool."""
    owner.floating_mana["Green"] += 1


TapForGreen = Ability(
    is_mana_ability=True,
    can_activate=is_not_tapped,
    pay_cost=tap_card,
    activity=add_g_mana,
)
