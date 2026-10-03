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

    mock_bear.reset()

    assert buff_1 not in mock_bear.modifiers
    assert buff_2 not in mock_bear.modifiers
    assert mock_bear != buff_1.target
    assert mock_bear != buff_2.target


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

    assert trample.target is None
    assert buff.target is None

    for c in game.p1.creatures:
        assert not c.has_trample()
        assert len(c.modifiers) == 0
        assert buff not in c.modifiers
        assert trample not in c.modifiers
