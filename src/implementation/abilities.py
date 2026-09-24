from src.Magic.Ability import Ability
from src.Magic.Card import Card, Creature, Instant, Sorcery
from src.Player.Player import Player
from src.Magic.Buff import Buff


# CAN ACTIVATE

def not_tapped_and_on_field(source: Card, owner: Player, opponent: Player) -> bool:
    """Check if the card is untapped and on the field."""
    return not source.tapped and source in owner.creatures + owner.lands

def fight_has_targets(source: Card, owner: Player, opponent: Player) -> bool:
    """Check if the player and opponent both control at least one Creature."""
    return len(owner.creatures) > 0 and len(opponent.creatures) > 0

def one_creature_exists(source: Card, owner: Player, opponent: Player) -> bool:
    """Check if at least one targettable Creature exists."""
    # ToDo: shroud & hexproof
    return len(owner.creatures) > 0 or len(opponent.creatures) > 0

def always_castable(source: Card, owner: Player, opponent: Player) -> bool:
    """Check nothing. Return True."""
    return True

# PAY COST

def tap_card(source: Card, owner: Player, opponent: Player) -> None:
    """Tap the source."""
    source.tapped = True

def target_single_creature_or_player(source: Card, owner: Player, opponent: Player) -> None:
    """Choose any target that has life."""
    assert isinstance(source, (Instant, Sorcery))
    target = owner.target(
        opp=opponent,
        own_player=True,
        own_creatures=True,
        opp_player=True,
        opp_creatures=True,    
    )
    assert isinstance(target, (Card, Player))
    source.targets = [target]

def target_single_creature(source: Card, owner: Player, opponent: Player) -> None:
    """Choose a target creature."""
    assert isinstance(source, (Instant, Sorcery))
    target = owner.target(
        opp=opponent, 
        own_creatures=True, 
        opp_creatures=True,
    )
    assert isinstance(target, Card)
    source.targets = [target]

def collect_fight_targets(source: Instant | Sorcery, owner: Player, opponent: Player) -> None:
    """Choose two creatures for fight effect."""
    assert isinstance(source, (Instant, Sorcery))
    puncher = owner.target(own_creatures=True)
    bag = owner.target(opp=opponent, opp_creatures=True)
    source.targets = [puncher, bag]

# EFFECT

def add_g_mana(source: Card, owner: Player, opponent: Player) -> None:
    """Add one Green Mana to the owners Manapool."""
    print(f"[MANA] tapping {source.name} for G")
    owner.floating_mana["Green"] += 1

def add_r_mana(source: Card, owner: Player, opponent: Player) -> None:
    """Add one Green Mana to the owners Manapool."""
    print(f"[MANA] tapping {source.name} for R.")
    owner.floating_mana["Red"] += 1

def punch(source: Instant | Sorcery, owner: Player, opponent: Player) -> None:
    """Puncher deals dmg equal to its power to Bag."""
    assert isinstance(source, (Instant, Sorcery))
    assert len(source.targets) == 2
    puncher: Creature = source.targets[0]
    bag: Creature = source.targets[1]
    if puncher in owner.creatures and bag in opponent.creatures:
        bag.damage_counter += puncher.get_power()

def bolt(source: Card, owner: Player, opponent: Player) -> None:
    """Deal 3 damage to the sources target."""
    assert isinstance(source, (Instant, Sorcery))
    assert len(source.targets) == 1
    target = source.targets[0]
    assert isinstance(target, (Player, Creature)), target
    if isinstance(target, Player):
        target.life -= 3
    if isinstance(target, Creature):
        target.damage_counter += 3

def eot_p3p3(source: Card, owner: Player, opponent: Player) -> None:
    """Target creature gets +3/+3 until end of turn."""
    assert isinstance(source, (Instant, Sorcery))
    assert len(source.targets) == 1
    target = source.targets[0]
    assert isinstance(target, Creature)
    buff = Buff(target=target, power=3, toughness=3)
    owner.eot_effects.append(buff)
    target.buffs.append(buff)

# INSTANCES

TapForGreen = Ability(
    is_mana_ability=True,
    mana_color="Green",
    can_activate=not_tapped_and_on_field,
    pay_cost=tap_card,
    activity=add_g_mana,
)

TapForRed = Ability(
    is_mana_ability=True,
    mana_color="Red",
    can_activate=not_tapped_and_on_field,
    pay_cost=tap_card,
    activity=add_r_mana,
)

Punch = Ability(
    is_mana_ability=False,
    can_activate=fight_has_targets,
    pay_cost=collect_fight_targets,
    activity=punch,
)

Bolt = Ability(
    is_mana_ability=False,
    can_activate=always_castable,
    pay_cost=target_single_creature_or_player,
    activity=bolt,
)

GiantGrowth = Ability(
    is_mana_ability=False,
    can_activate=one_creature_exists,
    pay_cost=target_single_creature,
    activity=eot_p3p3,
)
