import sys
import pytest
import random
from unittest.mock import MagicMock, Mock
from pathlib import Path

from conftest import build_priority_data

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.Magic.Game import Game
from src.Magic.Modifier import Modifier
from src.Magic.Library import load_from_decklist
from src.Magic.Card import Card, Land, Spell, Creature, Instant, Sorcery
from src.Magic.Stack import PriorityData
from src.Magic.Ability import Ability
from src.Magic.Stack import StackObject
from src.Magic.Cost import Cost
from src.Player.Player import Player
from src.implementation.cards import get_card


# PRIEST OF TITANIA

def test_priest_of_titania_makes_multiple_mana(game, mock_elf_dork_factory):
    """With 5 elves on the field, titania should generate 5 {G}."""
    pot = get_card("Priest_of_Titania")
    game.p1.creatures = [mock_elf_dork_factory() for _ in range(4)]
    game.p1.creatures.append(pot)

    pot.activated_ability.activity(pot, game.p1, game.p2, [])

    assert game.p1.floating_mana["Green"] == 5

def test_priest_of_titania_counts_opponents_elves(game, mock_elf_dork_factory):
    """With 5 elves on the field, titania should generate 5 {G}."""
    pot = get_card("Priest_of_Titania")
    game.p2.creatures = [mock_elf_dork_factory() for _ in range(4)]
    game.p1.creatures.append(pot)

    pot.activated_ability.activity(pot, game.p1, game.p2, [])

    assert game.p1.floating_mana["Green"] == 5

# TIMBERWATCH ELF

def test_timberwatch_elf_modifies_some_creature(game, mock_bear):
    twe = get_card("Timberwatch_Elf")
    game.p1.creatures = [twe, mock_bear]
    targets = [mock_bear]

    twe.activated_ability.activity(twe, game.p1, game.p2, targets)

    assert len(mock_bear.modifiers) == 1
    assert len(game.p1.eot_effects) == 1
    assert mock_bear.get_power() == mock_bear.base_power + 1
    assert mock_bear.get_toughness() == mock_bear.base_toughness + 1

def test_timberwatch_elf_modifies_proportional_to_elves(game, mock_bear, mock_elf_dork_factory):
    twe = get_card("Timberwatch_Elf")
    game.p1.creatures = [twe, mock_bear, mock_elf_dork_factory(), mock_elf_dork_factory()]
    game.p2.creatures = [mock_elf_dork_factory(), mock_elf_dork_factory()]
    targets = [mock_bear]

    twe.activated_ability.activity(twe, game.p1, game.p2, targets)

    assert len(mock_bear.modifiers) == 1
    assert len(game.p1.eot_effects) == 1
    assert mock_bear.get_power() == mock_bear.base_power + 5
    assert mock_bear.get_toughness() == mock_bear.base_toughness + 5
    assert mock_bear.modifiers[0].power == 5
    assert mock_bear.modifiers[0].toughness == 5

def test_two_twe_buffs_are_cleared_correctly(game, mock_bear):
    twe_1 = get_card("Timberwatch_Elf")
    twe_2 = get_card("Timberwatch_Elf")

    twe_1.activated_ability.activity(twe_1, game.p1, game.p2, [mock_bear])
    twe_2.activated_ability.activity(twe_2, game.p1, game.p2, [mock_bear])

    assert len(mock_bear.modifiers) == 2
    assert len(game.p1.eot_effects) == 2

    buff_1 = game.p1.eot_effects[0]
    buff_2 = game.p1.eot_effects[1]
    assert buff_1 in mock_bear.modifiers
    assert buff_2 in mock_bear.modifiers
    assert mock_bear in buff_1.target
    assert mock_bear in buff_2.target

    mock_bear.reset()

    assert buff_1 not in mock_bear.modifiers
    assert buff_2 not in mock_bear.modifiers
    assert mock_bear not in buff_1.target
    assert mock_bear not in buff_2.target


# SPECTRAL HUNT CALLER

def test_shc_buffs_all_owners_creatures(game, mock_bear_factory):
    shc = get_card("Spectral_Hunt-Caller")
    bear_1 = mock_bear_factory()
    bear_2 = mock_bear_factory()
    game.p1.creatures = [shc, bear_1, bear_2]

    shc.activated_ability.activity(shc, game.p1, game.p2, [])

    assert shc.has_trample()
    assert bear_1.has_trample()
    assert bear_2.has_trample()
    assert len(bear_1.modifiers) == 2
    assert len(bear_2.modifiers) == 2
    assert len(shc.modifiers) == 2
    assert bear_1.modifiers[0] == bear_2.modifiers[0]
    assert len(game.p1.eot_effects) == 2

def test_shc_does_not_buff_creatures_entered_later(game, mock_bear_factory):
    shc = get_card("Spectral_Hunt-Caller")
    early_bear = mock_bear_factory()
    game.p1.creatures = [shc, early_bear]

    shc.activated_ability.activity(shc, game.p1, game.p2, None)

    assert len(game.p1.eot_effects) == 2
    buff = game.p1.eot_effects[0]
    trample = game.p1.eot_effects[1]

    late_bear = mock_bear_factory()
    game.p1.creatures.append(late_bear)

    assert late_bear not in buff.target
    assert buff not in late_bear.modifiers

def test_shc_buffs_is_resetted_correctly(game, mock_bear_factory):
    shc = get_card("Spectral_Hunt-Caller")
    bear_1 = mock_bear_factory()
    bear_2 = mock_bear_factory()
    game.p1.creatures = [shc, bear_1, bear_2]

    shc.activated_ability.activity(shc, game.p1, game.p2, None)
    
    assert len(game.p1.eot_effects) == 2
    buff = game.p1.eot_effects[0]
    trample = game.p1.eot_effects[1]

    for c in game.p1.creatures:
        assert c.has_trample()
        assert len(c.modifiers) == 2
        assert buff in c.modifiers
        assert trample in c.modifiers
        assert c in buff.target
        assert c in trample.target

    bear_1.reset()

    assert buff not in bear_1.modifiers
    assert trample not in bear_1.modifiers
    assert not bear_1.has_trample()
    assert len(bear_1.modifiers) == 0
    assert buff not in bear_1.modifiers
    assert trample not in bear_1.modifiers
    assert bear_1 not in buff.target
    assert bear_1 not in trample.target

def test_shc_buffs_is_cleaned_up_correctly(game, mock_bear_factory):
    shc = get_card("Spectral_Hunt-Caller")
    bear_1 = mock_bear_factory()
    bear_2 = mock_bear_factory()
    game.p1.creatures = [shc, bear_1, bear_2]

    shc.activated_ability.activity(shc, game.p1, game.p2, None)
    
    assert len(game.p1.eot_effects) == 2
    buff = game.p1.eot_effects[0]
    trample = game.p1.eot_effects[1]

    for c in game.p1.creatures:
        assert c.has_trample()
        assert len(c.modifiers) == 2
        assert buff in c.modifiers
        assert trample in c.modifiers
        assert c in buff.target
        assert c in trample.target

    game.cleanup_step()

    assert trample.target == []
    assert buff.target == []

    for c in game.p1.creatures:
        assert not c.has_trample()
        assert len(c.modifiers) == 0
        assert buff not in c.modifiers
        assert trample not in c.modifiers
        assert c not in trample.target
        assert c not in buff.target

# GENEROUS ENT

def test_ent_creates_food(game):
    ent = get_card("Generous_Ent")
    game.stack = [StackObject("Cast", ent, game.p1)]
    data = build_priority_data(game)

    game.resolve_top_object_from_stack(data)

    assert len(game.stack) == 1
    so = game.stack[0]
    assert so.action == "EtbAbility"
    assert so.source == ent

    game.resolve_top_object_from_stack(data)

    assert len(game.stack) == 0
    assert len(game.p1.nc_permanents) == 1, "Food should have been created"

def test_ent_cycling_is_generated(mock_player):
    ent = get_card("Generous_Ent")
    mock_player.hand = [ent]
    actions = mock_player.collect_activated_abilities()

    assert len(actions) == 1
    action, source = actions[0]
    assert action == "Ability"
    assert source == ent

# LEAD THE STAMPEDE

def test_lts_only_bears(mock_player, mock_bear_factory):
    lts = get_card("Lead_the_Stampede")
    mock_player.library = [mock_bear_factory() for _ in range(5)]
    mock_player.hand = []

    assert len(mock_player.library) == 5

    lts.ability.activity(lts, mock_player, None, None)

    print(mock_player.hand)
    assert len(mock_player.hand) == 5
    assert len(mock_player.library) == 0

    for c in mock_player.hand:
        assert isinstance(c, Creature)

def test_lts_mixed(mock_player, mock_land, mock_bolt, mock_sorcery, mock_artifact, mock_bear):
    lts = get_card("Lead_the_Stampede")
    mock_player.library = [mock_land, mock_bolt, mock_sorcery, mock_artifact, mock_bear]
    mock_player.hand = []

    assert len(mock_player.library) == 5

    lts.ability.activity(lts, mock_player, None, None)

    print(mock_player.hand)
    assert len(mock_player.hand) == 1
    assert len(mock_player.library) == 4

    for c in mock_player.hand:
        assert isinstance(c, Creature)

def test_lts_lib_size(mock_player, mock_bear_factory):
    lts = get_card("Lead_the_Stampede")
    mock_player.library = [mock_bear_factory() for _ in range(40)]
    mock_player.hand = []

    assert len(mock_player.library) == 40

    lts.ability.activity(lts, mock_player, None, None)

    print(mock_player.hand)
    assert len(mock_player.hand) == 5
    assert len(mock_player.library) == 35

    for c in mock_player.hand:
        assert isinstance(c, Creature)


# KESSIG FLAMEBREATHER

def test_bolt_triggers_kessig(game):
    kf = get_card("Kessig_Flamebreather")
    bolt = get_card("Lightning_Bolt")
    game.p1.target = MagicMock(return_value=[])
    game.p1.put_creature_onto_field(kf)
    game.p1.hand = [bolt]
    data = build_priority_data(game)
    game.p1.pay_for_manacost = MagicMock(retur_value=True)

    assert kf in game.p1.triggered_abilities

    game.cast_spell(data, bolt)

    print(game.stack)

    assert len(game.stack) == 2
    assert game.stack[0].source == bolt
    assert game.stack[1].source == kf

def test_bear_not_triggers_kessig(game, mock_bear):
    kf = get_card("Kessig_Flamebreather")
    game.p1.target = MagicMock(return_value=[])
    game.p1.put_creature_onto_field(kf)
    game.p1.hand = [mock_bear]
    data = build_priority_data(game)
    game.p1.pay_for_manacost = MagicMock(return_value=True)

    assert kf in game.p1.triggered_abilities

    game.cast_spell(data, mock_bear)

    print(game.stack)

    assert len(game.stack) == 1
    assert game.stack[0].source == mock_bear

def test_flashback_triggers_kessig(game):
    kf = get_card("Kessig_Flamebreather")
    fl: Sorcery = get_card("Faithless_Looting")
    fl.ability.activity = MagicMock()
    game.p1.put_creature_onto_field(kf)
    game.p1.graveyard = [fl]
    data = build_priority_data(game)
    game.p1.pay_for_manacost = MagicMock(return_valur=True)

    game.cast_spell(data, fl, "CastFlashback")

    game.p1.graveyard == []
    assert len(game.stack) == 2
    assert game.stack[0].source == fl
    assert game.stack[1].source == kf


# FIRE BLAST

def test_fireblast_hardcast_successfully(game, mock_bear, mock_ability):
    fb = get_card("Fire_Blast")
    fb.ability = mock_ability
    targets = [mock_bear]
    fb.ability.choose_targets = MagicMock(return_value=targets)

    assert isinstance(fb.cost, list)
    cost = fb.cost[0]
    assert isinstance(cost, Cost)
    assert cost.can_pay_extra_cost is None
    assert cost.pay_extra_cost is None

    # choose to pay 6 mana
    game.determine_cost = MagicMock(return_value=cost)
    game.put_action_on_stack = MagicMock()
    game.p1.hand = [fb]
    game.p2.put_creature_onto_field(mock_bear)
    game.p1.pay_for_manacost = MagicMock(return_value=True)
    data = build_priority_data(game)

    game.cast_spell(data, fb)

    fb.ability.can_activate.assert_called_once_with(
        fb, data.priority_player, data.non_priority_player,
    )
    fb.ability.choose_targets.assert_called_once_with(
        fb, data.priority_player, data.non_priority_player,
    )
    game.determine_cost.assert_called_once_with(fb, data.priority_player, "Cast")
    
    game.p1.pay_for_manacost.assert_called_once_with(
        cost.mana_cost, data.non_priority_player,
    )
    fb.ability.pay_cost.assert_called_once_with(
        fb, data.priority_player, data.non_priority_player, targets,
    )
    assert fb not in game.p1.hand
    assert fb not in game.p1.graveyard
    game.put_action_on_stack.assert_called_once_with(
        data, "Cast", fb, targets,
    )

def test_fireblast_altcost_cast_successfully(game, mock_bear, mock_ability, mock_cost):
    fb = get_card("Fire_Blast")
    fb.ability = mock_ability
    targets = [mock_bear]
    fb.ability.choose_targets = MagicMock(return_value=targets)

    assert isinstance(fb.cost, list)
    assert isinstance(fb.cost[1], Cost)
    fb.cost[1].can_pay_extra_cost = MagicMock(return_value=True)
    fb.cost[1].pay_extra_cost = MagicMock()
    cost = fb.cost[1]
    assert cost.has_extra_cost

    # choose to sac 2 mountains
    game.determine_cost = MagicMock(return_value=cost)
    game.put_action_on_stack = MagicMock()
    game.p1.hand = [fb]
    game.p1.put_land_onto_field(get_card("Mountain"))
    game.p1.put_land_onto_field(get_card("Mountain"))
    game.p2.put_creature_onto_field(mock_bear)
    game.p1.pay_for_manacost = MagicMock(return_value=True)
    data = build_priority_data(game)

    game.cast_spell(data, fb)

    fb.ability.can_activate.assert_called_once_with(
        fb, data.priority_player, data.non_priority_player,
    )
    fb.ability.choose_targets.assert_called_once_with(
        fb, data.priority_player, data.non_priority_player,
    )
    game.determine_cost.assert_called_once_with(fb, data.priority_player, "Cast")

    cost.can_pay_extra_cost.assert_called_once_with(
        fb, game.p1, game.p2, targets,
    )
    cost.pay_extra_cost.assert_called_once_with(
        fb, game.p1, game.p2, targets,
    )
    
    game.p1.pay_for_manacost.assert_not_called()
    fb.ability.pay_cost.assert_called_once_with(
        fb, data.priority_player, data.non_priority_player, targets,
    )
    assert fb not in game.p1.hand
    assert fb not in game.p1.graveyard
    game.put_action_on_stack.assert_called_once_with(
        data, "Cast", fb, targets,
    )

def test_fireblast_sacs_two_mountains(game):
    fb = get_card("Fire_Blast")
    m1 = get_card("Mountain")
    m2 = get_card("Mountain")
    game.p1.hand = [fb]
    game.p1.put_land_onto_field(m1)
    game.p1.put_land_onto_field(m2)
    game.p1.target = MagicMock(side_effect=[game.p2, m1, m2])
    game.p1.choose_int_value = MagicMock(return_value=1)
    data = build_priority_data(game)

    game.cast_spell(data, fb)

    assert game.p1.lands == []
    assert len(game.p1.graveyard) == 2
    assert game.p1.graveyard[0] == m1
    assert game.p1.graveyard[1] == m2


# FAITHLESS LOOTING

def test_faithless_looting(game):
    fl: Sorcery = get_card("Faithless_Looting")
    game.p1.target = MagicMock()
    game.p1.draw = MagicMock()
    game.p1.discard_one_card = MagicMock()

    fl.ability.activity(fl, game.p1, game.p2, None)

    game.p1.draw.assert_called_once_with(2)
    assert game.p1.discard_one_card.call_count == 2

def test_flashback_looting(game):
    fl: Sorcery = get_card("Faithless_Looting")
    fl.ability.activity = MagicMock()
    game.p1.graveyard = [fl]
    so = StackObject("CastFlashback", fl, game.p1, None)
    data = build_priority_data(game)

    game.stack = [so]
    game.resolve_top_object_from_stack(data)

    game.p1.graveyard == []
    fl.ability.activity.assert_called_once()


# GRAB THE PRICE

def test_gtp_can_activate(game, mock_bear):
    gtp: Sorcery = get_card("Grab_the_Price")
    game.p1.hand = [gtp, mock_bear]

    assert gtp.ability.can_activate(gtp, game.p1, game.p2)

def gtp_cant_discard_self(game, mock_bear):
    gtp: Sorcery = get_card("Grab_the_Price")
    game.p1.hand = [gtp, mock_bear]

    targets = gtp.ability.choose_targets(gtp, game.p1, game.p2)

    assert targets == [mock_bear]

def gtp_cannot_activate_with_only_self_in_hand(game):
    gtp: Sorcery = get_card("Grab_the_Price")
    game.p1.hand = [gtp]
    
    assert not gtp.ability.can_activate(game, game.p1, game.p2)
