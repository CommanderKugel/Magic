from Magic.Ability import Ability
from Magic.Card import Card, Creature, Instant, Sorcery
from Player.Player import Player


# CAN ACTIVATE

def not_tapped_and_on_field(source: Card, owner: Player, opponent: Player) -> bool:
    """Check if the card is untapped and on the field."""
    return (
        not source.tapped
        and source in owner.creatures + owner.lands
    )

def fight_has_targets(source: Card, owner: Player, opponent: Player) -> bool:
    """Check if the player and opponent both control at least one Creature."""
    return (
        len(owner.creatures) > 0
        and len(opponent.creatures) > 0
    )

# PAY COST

def tap_card(source: Card, owner: Player, opponent: Player) -> None:
    """Tap the source."""
    source.tapped = True

def collect_fight_targets(source: Instant | Sorcery, owner: Player, opponent: Player) -> None:
    """Choose two creatures for fight effect."""
    assert isinstance(source, (Instant, Sorcery))
    puncher = owner.target(own_creatures=True)
    bag = owner.target(opp=opponent, opp_creatures=True)
    source.targets = [puncher, bag]

# EFFECT

def punch(source: Instant | Sorcery, owner: Player, opponent: Player) -> None:
    """Puncher deals dmg equal to its power to Bag."""
    assert isinstance(source, (Instant, Sorcery))
    assert len(source.targets) == 2
    puncher: Creature = source.targets[0]
    bag: Creature = source.targets[1]
    if puncher in owner.creatures and bag in opponent.creatures:
        bag.damage_counter += puncher.power

def add_g_mana(source: Card, owner: Player, opponent: Player) -> None:
    """Add one Green Mana to the owners Manapool."""
    owner.floating_mana["Green"] += 1


TapForGreen = Ability(
    is_mana_ability=True,
    can_activate=not_tapped_and_on_field,
    pay_cost=tap_card,
    activity=add_g_mana,
)

Punch = Ability(
    is_mana_ability=False,
    can_activate=fight_has_targets,
    pay_cost=collect_fight_targets,
    activity=punch,
)
