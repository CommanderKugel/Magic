from src.Magic.Ability import Ability
from src.Magic.Card import Card, Land, Artifact, Creature, Instant, Sorcery
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

def creature_is_on_field(source: Creature, owner: Player, opponent: Player) -> bool:
    """Checks if the creature is on the board."""
    return source in owner.creatures

def artifact_can_tap_own_creature(source: Artifact, owner: Player, opponent: Player) -> bool:
    """Springleaf drum."""
    return (
        source in owner.nc_permanents
        and any(c for c in owner.creatures if not c.tapped)
    )

def one_creature_exists(source: Card, owner: Player, opponent: Player) -> bool:
    """Check if at least one targettable Creature exists."""
    # ToDo: shroud & hexproof
    return len(owner.creatures) > 0 or len(opponent.creatures) > 0

def fight_has_targets(source: Card, owner: Player, opponent: Player) -> bool:
    """Check if the player and opponent both control at least one Creature."""
    # ToDo: hexproof & shroud
    return len(owner.creatures) > 0 and len(opponent.creatures) > 0

# SELECT TARAGETS

def no_targets(source: Card, owner: Player, opponent: Player) -> list[Card | Player] | None:
    """Card does not target anything."""
    return None

def target_single_creature(source: Card, owner: Player, opponent: Player) -> list[Card | Player]:
    """Choose a target creature."""
    target = owner.target(
        opp=opponent, 
        own_creatures=True, 
        opp_creatures=True,
    )
    return [target]

def target_untapped_creature_from_owner(source: Card, owner: Player, opponent: Player) -> list[Card]:
    """Choose one creature that the owner controls. Does not target that creature."""
    def untapped_creatures(l: list[Creature]) -> list[Creature]:
        return [c for c in l if isinstance(c, Creature) and not c.tapped]
    target = owner.target(own_creatures=True, filter=untapped_creatures)
    return [target]

def target_single_creature_or_player(source: Card, owner: Player, opponent: Player) -> list[Card | Player]:
    """Choose any target that can take damage."""
    target = owner.target(
        opp=opponent,
        own_player=True,
        own_creatures=True,
        opp_player=True,
        opp_creatures=True,    
    )
    return [target]

def target_two_creatures_to_fight(source: Card, owner: Player, opponent: Player) -> list[Card | Player]:
    """Target one creature the owner controls and one creature the opponent controls."""
    puncher = owner.target(own_creatures=True)
    bag = owner.target(opp=opponent, opp_creatures=True)
    return [puncher, bag]

# PAY COST

def no_cost(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Ability does not require an additional cost."""
    return None

def tap_card(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Tap the source."""
    source.tapped = True

def tap_card_and_chosen_creature(source: Card, owner: Player, opponent: Player, targets: list[Creature]) -> None:
    """Tap the chosen creature."""
    target = targets[0]
    target.tapped = True
    source.tapped = True

# ACTIVITY

def add_g_mana(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Add one Green Mana to the owners Manapool."""
    owner.floating_mana["Green"] += 1

def add_r_mana(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Add one Green Mana to the owners Manapool."""
    owner.floating_mana["Red"] += 1

def add_mana_of_any_color(source: Card, owner: Player, opponent: Player) -> None:
    """Add one mana of any Color."""
    color = owner.choose_color(["White", "Blue", "Black", "Red", "Green"])

def punch(source: Instant | Sorcery, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Puncher deals dmg equal to its power to Bag."""
    assert isinstance(source, (Instant, Sorcery))
    assert len(targets) == 2
    puncher: Creature = targets[0]
    bag: Creature = targets[1]
    if puncher in owner.creatures and bag in opponent.creatures:
        bag.damage_counter += puncher.get_power()

def bolt(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Deal 3 damage to the sources target."""
    target = targets[0]
    if isinstance(target, Player):
        target.life -= 3
    elif isinstance(target, Creature):
        if (
            target in opponent.creatures
            or target in owner.creatures
        ):
            target.damage_counter += 3
    
def eot_p3p3(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Target creature gets +3/+3 until end of turn."""
    target: Creature = targets[0]
    buff = Buff(target=target, power=3, toughness=3)
    owner.eot_effects.append(buff)
    target.modifiers.append(buff)

def eot_p3p3_for_source(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Target creature gets +3/+3 until end of turn."""
    target: Creature = source
    buff = Buff(target=target, power=3, toughness=3)
    owner.eot_effects.append(buff)
    target.modifiers.append(buff)

def eot_p3p3_and_trample(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Target Creature gets +3/+3 and trample until end of turn."""
    target: Creature = targets[0]
    buff = Buff(target=target, power=3, toughness=3)
    trample = KeywordBuff(target=target, trample=True)
    owner.eot_effects.append(buff)
    owner.eot_effects.append(trample)
    target.modifiers.append(buff)
    target.modifiers.append(trample)

def add_g_for_number_of_elves(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Player gets X times {G} where X is the numer of elves on the battlefield."""
    elf_count = sum(1 for c in owner.creatures + opponent.creatures if "Elf" in c.subtype)
    owner.floating_mana["Green"] += elf_count

def eot_add_p1p1_for_number_of_elves(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """Creature gets +X/+X where X is the numer of elves on the battlefield."""
    x = sum(1 for c in owner.creatures + opponent.creatures if "Elf" in c.subtype)
    target: Creature = targets[0]
    buff = Buff(target=target, power=x, toughness=x)
    owner.eot_effects.append(buff)
    target.modifiers.append(buff)

def eot_owners_creatures_gain_p1p1_and_trample(source: Card, owner: Player, opponent: Player, targets: list[Creature | Player] | None) -> None:
    """All Creatures owner controls get +1/+1 and trample until end of turn."""
    targets = owner.creatures.copy()
    p1p1 = Buff(target=targets, power=1, toughness=1)
    trample = KeywordBuff(target=targets, trample=True)

    owner.eot_effects.append(p1p1)
    owner.eot_effects.append(trample)

    for creature in targets:
        creature.modifiers.append(p1p1)
        creature.modifiers.append(trample)

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

SpectralHuntCaller = Ability(
    mana_cost={"Green": 1, "None": 5},
    _can_activate=creature_is_on_field,
    _choose_targets=no_targets,
    _pay_cost=no_cost,
    _activity=eot_owners_creatures_gain_p1p1_and_trample,
)

SpringleafDrum = Ability(
    is_mana_ability=True,
    mana_color=["White", "Blue", "Black", "Red", "Green"],
    _can_activate=artifact_can_tap_own_creature,
    _choose_targets=target_untapped_creature_from_owner,
    _pay_cost=tap_card_and_chosen_creature,
    _activity=add_mana_of_any_color,
)
