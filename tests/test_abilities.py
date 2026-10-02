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
