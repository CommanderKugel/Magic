from Magic.Ability import Ability
from Magic.Card import Card
from Player.Player import Player


def not_tapped_and_on_field(source: Card, owner: Player) -> bool:
    """Check if the card is untapped and on the field."""
    return (
        not source.tapped
        and source in owner.creatures + owner.lands
    )

def tap_card(source: Card, owner: Player) -> None:
    """Tap the source."""
    source.tapped = True

def add_g_mana(source: Card, owner: Player) -> None:
    """Add one Green Mana to the owners Manapool."""
    owner.floating_mana["Green"] += 1


TapForGreen = Ability(
    is_mana_ability=True,
    can_activate=not_tapped_and_on_field,
    pay_cost=tap_card,
    activity=add_g_mana,
)
