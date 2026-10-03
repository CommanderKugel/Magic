from src.Magic.Ability import Ability
from src.Magic.Card import Card, Land, Creature, Instant, Sorcery
from src.Player.Player import Player
from src.Magic.Modifier import Modifier, Buff, KeywordBuff


# CAN ACTIVATE

def always_castable(source: Card, owner: Player, opponent: Player) -> bool:
    """Card can always be cast."""
    return True

def land_is_untapped_and_on_field(source: Land, owner: Player, opponent: Player) -> bool:
    """Check if the land is untapped and on the field."""
    return not source.tapped and source in owner.lands

def creature_can_tap_and_on_field(source: Creature, owner: Player, opponent: Player) -> bool:
    """Check if the card is untapped and on the field."""
    return not source.tapped and not source.summoning_sick and source in owner.creatures

def one_creature_exists(source: Card, owner: Player, opponent: Player) -> bool:
    """Check if at least one targettable Creature exists."""
    # ToDo: shroud & hexproof
    return len(owner.creatures) > 0 or len(opponent.creatures) > 0

def fight_has_targets(source: Card, owner: Player, opponent: Player) -> bool:
    """Check if the player and opponent both control at least one Creature."""
    # ToDo: hexproof & shroud
    return len(owner.creatures) > 0 and len(opponent.creatures) > 0

# SELECT TARAGETS

def no_targets(source: Card, owner: Player, opponent: Player) -> None:
    """Card does not target anything."""
    return None

def target_single_creature(source: Card, owner: Player, opponent: Player) -> None:
    """Choose a target creature."""
    target = owner.target(
        opp=opponent, 
        own_creatures=True, 
        opp_creatures=True,
    )
    source.targets = [target]

def target_single_creature_or_player(source: Card, owner: Player, opponent: Player) -> None:
    """Choose any target that can take damage."""
    target = owner.target(
        opp=opponent,
        own_player=True,
        own_creatures=True,
        opp_player=True,
        opp_creatures=True,    
    )
    source.targets = [target]

def target_two_creatures_to_fight(source: Card, owner: Player, opponent: Player) -> None:
    """Target one creature the owner controls and one creature the opponent controls."""
    puncher = owner.target(own_creatures=True)
    bag = owner.target(opp=opponent, opp_creatures=True)
    source.targets = [puncher, bag]

# PAY COST

def no_cost(source: Card, owner: Player, opponent: Player) -> None:
    """Ability does not require an additional cost."""
    return None

def tap_card(source: Card, owner: Player, opponent: Player) -> None:
    """Tap the source."""
    source.tapped = True

# ACTIVITY

def add_g_mana(source: Card, owner: Player, opponent: Player) -> None:
    """Add one Green Mana to the owners Manapool."""
    owner.floating_mana["Green"] += 1

def add_r_mana(source: Card, owner: Player, opponent: Player) -> None:
    """Add one Green Mana to the owners Manapool."""
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
    target = source.targets[0]
    if isinstance(target, Player):
        target.life -= 3
    elif isinstance(target, Creature):
        if (
            target in opponent.creatures
            or target in owner.creatures
        ):
            target.damage_counter += 3
    
def eot_p3p3(source: Card, owner: Player, opponent: Player) -> None:
    """Target creature gets +3/+3 until end of turn."""
    target: Creature = source.targets[0]
    buff = Buff(target=target, power=3, toughness=3)
    owner.eot_effects.append(buff)
    target.modifiers.append(buff)

def eot_p3p3_for_source(source: Card, owner: Player, opponent: Player) -> None:
    """Target creature gets +3/+3 until end of turn."""
    target: Creature = source
    buff = Buff(target=target, power=3, toughness=3)
    owner.eot_effects.append(buff)
    target.modifiers.append(buff)

def eot_p3p3_and_trample(source: Card, owner: Player, opponent: Player) -> None:
    """Target Creature gets +3/+3 and trample until end of turn."""
    target: Creature = source.targets[0]
    buff = Buff(target=target, power=3, toughness=3)
    trample = KeywordBuff(target=target, trample=True)
    owner.eot_effects.append(buff)
    owner.eot_effects.append(trample)
    target.modifiers.append(buff)
    target.modifiers.append(trample)

def add_g_for_number_of_elves(source: Card, owner: Player, opponent: Player) -> None:
    """Player gets X times {G} where X is the numer of elves on the battlefield."""
    elf_count = sum(1 for c in owner.creatures + opponent.creatures if "Elf" in c.subtype)
    owner.floating_mana["Green"] += elf_count

def eot_add_p1p1_for_number_of_elves(source: Card, owner: Player, opponent: Player) -> None:
    """Creature gets +X/+X where X is the numer of elves on the battlefield."""
    x = sum(1 for c in owner.creatures + opponent.creatures if "Elf" in c.subtype)
    target: Creature = source.targets[0]
    buff = Buff(target=target, power=x, toughness=x)
    owner.eot_effects.append(buff)
    target.modifiers.append(buff)

# INSTANCES

LandTapForGreen = Ability(
    is_mana_ability=True,
    mana_color="Green",
    _can_activate=land_is_untapped_and_on_field,
    _choose_targets=no_targets,
    _pay_cost=tap_card,
    _activity=add_g_mana,
)

LandTapForRed = Ability(
    is_mana_ability=True,
    mana_color="Red",
    _can_activate=land_is_untapped_and_on_field,
    _choose_targets=no_targets,
    _pay_cost=tap_card,
    _activity=add_r_mana,
)

CreatureTapForGreen = Ability(
    is_mana_ability=True,
    mana_color="Green",
    _can_activate=creature_can_tap_and_on_field,
    _choose_targets=no_targets,
    _pay_cost=tap_card,
    _activity=add_g_mana,
)

Punch = Ability(
    _can_activate=fight_has_targets,
    _choose_targets=target_two_creatures_to_fight,
    _pay_cost=no_cost,
    _activity=punch,
)

Bolt = Ability(
    _can_activate=always_castable, # ToDo: hexproof & shroud
    _choose_targets=target_single_creature_or_player,
    _pay_cost=no_cost,
    _activity=bolt,
)

GiantGrowth = Ability(
    _can_activate=one_creature_exists,
    _choose_targets=target_single_creature,
    _pay_cost=no_cost,
    _activity=eot_p3p3,
)

BlitzBallShot = Ability(
    _can_activate=one_creature_exists,
    _choose_targets=target_single_creature,
    _pay_cost=no_cost,
    _activity=eot_p3p3_and_trample,
)

AlmightyBrushwagg = Ability(
    _can_activate=always_castable,
    _choose_targets=no_targets,
    _pay_cost=no_cost,
    _activity=eot_p3p3_for_source,
    mana_cost={"Green": 1, "None": 3}
)

PriestOfTitania = Ability(
    is_mana_ability=True,
    mana_color="Green",
    _can_activate=creature_can_tap_and_on_field,
    _choose_targets=no_targets,
    _pay_cost=tap_card,
    _activity=add_g_for_number_of_elves,
)

TimberwatchElf = Ability(
    _can_activate=creature_can_tap_and_on_field,
    _choose_targets=target_single_creature,
    _pay_cost=tap_card,
    _activity=eot_add_p1p1_for_number_of_elves,
)
