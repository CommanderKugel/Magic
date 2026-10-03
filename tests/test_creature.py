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
        flying = KeywordBuff(target=mock_bear, flying=True)
        mock_bear.modifiers = [flying]
        assert mock_bear.is_flying()
        assert not mock_bear.has_trample()
        assert not mock_bear.has_reach()

    def test_keyword_buff_gives_trample(self, mock_bear):
        trample = KeywordBuff(target=mock_bear, trample=True)
        mock_bear.modifiers = [trample]
        assert mock_bear.has_trample()
        assert not mock_bear.is_flying()
        assert not mock_bear.has_reach()

    def test_keyword_buff_gives_reach(self, mock_bear):
        reach = KeywordBuff(target=mock_bear, reach=True)
        mock_bear.modifiers = [reach]
        assert mock_bear.has_reach()
        assert not mock_bear.is_flying()
        assert not mock_bear.has_trample()
