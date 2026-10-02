import sys
import pytest
import random
from unittest.mock import MagicMock, Mock
from pathlib import Path

from conftest import build_priority_data

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.Magic.Game import Game
from src.Magic.Buff import Buff
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

    pot.activated_ability.activity(pot, game.p1, game.p2)

    assert game.p1.floating_mana["Green"] == 5

def test_priest_of_titania_counts_opponents_elves(game, mock_elf_dork_factory):
    """With 5 elves on the field, titania should generate 5 {G}."""
    pot = get_card("Priest_of_Titania")
    game.p2.creatures = [mock_elf_dork_factory() for _ in range(4)]
    game.p1.creatures.append(pot)

    pot.activated_ability.activity(pot, game.p1, game.p2)

    assert game.p1.floating_mana["Green"] == 5

# TIMBERWATCH ELF

def test_timberwatch_elf_buffs_some_creature(game, mock_bear):
    twe = get_card("Timberwatch_Elf")
    game.p1.creatures = [twe, mock_bear]
    twe.targets = [mock_bear]

    twe.activated_ability.activity(twe, game.p1, game.p2)

    assert len(mock_bear.buffs) == 1
    assert len(game.p1.eot_effects) == 1
    assert mock_bear.get_power() == mock_bear.base_power + 1
    assert mock_bear.get_toughness() == mock_bear.base_toughness + 1

def test_timberwatch_elf_buffs_proportional_to_elves(game, mock_bear, mock_elf_dork_factory):
    twe = get_card("Timberwatch_Elf")
    game.p1.creatures = [twe, mock_bear, mock_elf_dork_factory(), mock_elf_dork_factory()]
    game.p2.creatures = [mock_elf_dork_factory(), mock_elf_dork_factory()]
    twe.targets = [mock_bear]

    twe.activated_ability.activity(twe, game.p1, game.p2)

    assert len(mock_bear.buffs) == 1
    assert len(game.p1.eot_effects) == 1
    assert mock_bear.get_power() == mock_bear.base_power + 5
    assert mock_bear.get_toughness() == mock_bear.base_toughness + 5
    assert mock_bear.buffs[0].power == 5
    assert mock_bear.buffs[0].toughness == 5
