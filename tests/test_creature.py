import sys
import pytest
import random
from unittest.mock import MagicMock, Mock
from pathlib import Path

from conftest import build_priority_data

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.Magic.Game import Game
from src.Magic.Modifier import Modifier, Buff, KeywordBuff
from src.Magic.Library import load_from_decklist
from src.Magic.Card import Card, Land, Spell, Creature, Instant, Sorcery
from src.Magic.Stack import PriorityData
from src.Magic.Ability import Ability
from src.Magic.Stack import StackObject
from src.Player.Player import Player
from src.implementation.cards import get_card


class TestCreatureKeywords:

    def test_vanilla_creature_has_no_keywords(self, mock_bear):
        assert not mock_bear.has_trample()
        assert not mock_bear.has_reach()
        assert not mock_bear.is_flying()

    def test_flyer_is_flying(self, mock_bear):
        mock_bear._flying = True
        assert mock_bear.is_flying()

    def test_trampler_has_trample(self, mock_bear):
        mock_bear._trample = True
        assert mock_bear.has_trample()

    def test_creature_with_reach_has_reach(self, mock_bear):
        mock_bear._reach = True
        assert mock_bear.has_reach()

    def test_keyword_buff_gives_flying(self, mock_bear):
        flying = KeywordBuff(target=[], flying=True)
        mock_bear.connect_modifier(flying)
        assert mock_bear.is_flying()
        assert not mock_bear.has_trample()
        assert not mock_bear.has_reach()

    def test_keyword_buff_gives_trample(self, mock_bear):
        trample = KeywordBuff(target=[], trample=True)
        mock_bear.connect_modifier(trample)
        assert mock_bear.has_trample()
        assert not mock_bear.is_flying()
        assert not mock_bear.has_reach()

    def test_keyword_buff_gives_reach(self, mock_bear):
        reach = KeywordBuff(target=[], reach=True)
        mock_bear.connect_modifier(reach)
        assert mock_bear.has_reach()
        assert not mock_bear.is_flying()
        assert not mock_bear.has_trample()

class TestCreatureReset:

    def test_reset_removes_creature_from_buff_targets(self, mock_bear):
        """A resetted creature can not be the target of a buff that targeted it before."""
        buff = Buff(target=[])
        mock_bear.connect_modifier(buff)

        mock_bear.reset()

        assert mock_bear not in buff.target
        assert buff not in mock_bear.modifiers

    def test_reset_removes_creature_from_buff_target_list(self, mock_bear_factory):
        """A resetted creature can not be the target of a buff that targeted it before."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        buff = Buff(target=[])
        bear_1.connect_modifier(buff)
        bear_2.connect_modifier(buff)

        bear_1.reset()

        assert bear_1 not in buff.target
        assert bear_2 in buff.target
        assert buff not in bear_1.modifiers
        assert buff in bear_2.modifiers

    def test_disconnect_removes_correct_mod_incase_of_duplicate_values(self, mock_bear):
        mod_1 = Buff(target=[], power=3, toughness=3)
        mod_2 = Buff(target=[], power=3, toughness=3)
        mock_bear.connect_modifier(mod_1)
        mock_bear.connect_modifier(mod_2)

        mock_bear.disconnect_modifier(mod_2)

        assert mod_1 in mock_bear.modifiers
        assert mod_2 not in mock_bear.modifiers
        assert mock_bear in mod_1.target
        assert mock_bear not in mod_2.target
