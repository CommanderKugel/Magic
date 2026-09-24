import sys
import pytest
import random
from unittest.mock import MagicMock, Mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.Magic.Game import Game
from src.Magic.Library import load_from_decklist
from src.Magic.Card import Card, Land, Spell, Creature, Instant, Sorcery
from src.Magic.Stack import PriorityData
from src.Magic.Ability import Ability
from src.Player.Player import Player
from src.implementation.cards import get_card

BEAR_LIST_PATH = Path(__file__).resolve().parent / "resources/bear_list.txt"


# Mock(side_effect=[("Cast", card), ("Pass", None)]) -> mock player.choose_action chains




@pytest.fixture
def game() -> Game:
    """Create minimal instance of game object. ATTENTION: players decks are empty!"""
    g = Game(
        p1=Player("P1", 20, []),
        p2=Player("P2", 20, []),
    )
    g.active_player = g.p1
    g.reactive_player = g.p2
    return g

@pytest.fixture
def mock_mana_ability() -> Ability:
    """Mock a mana ability."""
    return Ability(
        is_mana_ability=True,
        can_activate=MagicMock(return_value=True),
        pay_cost=MagicMock(),
        activity=MagicMock(),
    )

@pytest.fixture
def mock_ability() -> Ability:
    """Mock a non-mana ability."""
    return Ability(
        is_mana_ability=False,
        can_activate=MagicMock(return_value=True),
        pay_cost=MagicMock(),
        activity=MagicMock(),
    )

@pytest.fixture
def mock_land() -> Land:
    """Mock a land Card."""
    land = get_card("Forest")
    land.name = "mock_land"
    land.activated_ability = Ability(
        is_mana_ability=True,
        can_activate=MagicMock(return_value=True),
        pay_cost=MagicMock(),
        activity=MagicMock(),
    )
    return land

@pytest.fixture
def mock_bear(mock_ability) -> Creature:
    """Mock a vanilla creature."""
    creature = get_card("Balduvian_Bears")
    creature.name = "mock creature"
    creature.activated_ability = mock_ability
    return creature

@pytest.fixture
def mock_bolt(mock_ability) -> Instant:
    """Mock an instant spell."""
    instant: Instant = get_card("Lightning_Bolt")
    instant.ability = mock_ability
    return instant

@pytest.fixture
def mock_sorcery(mock_ability) -> Instant:
    """Mock an instant spell."""
    sorcery: Instant = get_card("Horrific_Assault")
    sorcery.ability = mock_ability
    return sorcery

def build_priority_data(game: Game) -> PriorityData:
    """Build minimal priority data object."""
    return PriorityData(
        state="Action",
        priority_player=game.p1,
        non_priority_player=game.p2,
    )


class TestHelperMethods:
    def test_play_land_happypath(self, game, mock_land):   
        """Playing a land makes the landdrop correctly."""
        data = build_priority_data(game)
        game.p1.hand = [mock_land]
        game.play_land(data, mock_land)
        assert mock_land not in game.p1.hand, "Land Should have been removed from Hand."
        assert mock_land in game.p1.lands, "Land should have appeard on the Field."
        assert game.hit_landdrop, "Landdrop has been made."

    def test_activate_mana_ability_can_activate(self, game, mock_land):
        """Activating a mana ability instantly resolves."""
        data = build_priority_data(game)
        game.activate_mana_ability(data, mock_land)
        mock_land.activated_ability.can_activate.assert_called_once()
        mock_land.activated_ability.pay_cost.assert_called_once_with(
            mock_land, data.priority_player, data.non_priority_player
        )
        mock_land.activated_ability.activity.assert_called_once_with(
            mock_land, data.priority_player, data.non_priority_player
        )

    def test_activate_mana_ability_can_not_activate(self, game, mock_land):
        """Mana ability cant activate and does not resolve."""
        mock_land.activated_ability.can_activate = MagicMock(return_value=False)
        data = build_priority_data(game)
        game.activate_mana_ability(data, mock_land)
        mock_land.activated_ability.can_activate.assert_called_once()
        mock_land.activated_ability.pay_cost.assert_not_called()
        mock_land.activated_ability.activity.assert_not_called()

    def test_activate_ability_can_activate(self, game, mock_bear):
        """Activating an ability puts it on the stack."""
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.activate_ability(data, mock_bear)
        mock_bear.activated_ability.can_activate.assert_called_once_with(
            mock_bear, data.priority_player, data.non_priority_player,
        )
        mock_bear.activated_ability.pay_cost.assert_called_once_with(
            mock_bear, data.priority_player, data.non_priority_player,
        )
        mock_bear.activated_ability.activity.assert_not_called()
        game.put_action_on_stack.assert_called_once_with(
            data, "Ability", mock_bear,
        )

    def test_activate_ability_can_not_activate(self, game, mock_bear):
        """Ability can not activate and is not put on the stack."""
        mock_bear.activated_ability.can_activate = MagicMock(return_value=False)
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.activate_ability(data, mock_bear)
        mock_bear.activated_ability.can_activate.assert_called_once_with(
            mock_bear, data.priority_player, data.non_priority_player,
        )
        mock_bear.activated_ability.pay_cost.assert_not_called()
        mock_bear.activated_ability.activity.assert_not_called()
        game.put_action_on_stack.assert_not_called()

    # NEXT - NEGATIVE TESTS FOR CASTING STUFF

    def test_cast_creature_successfully(self, game, mock_bear):
        """Creature is cast and put on the stack."""
        game.p1.hand = [mock_bear]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock()
        game.cast_spell(data, mock_bear)
        game.p1.pay_for_manacost.assert_called_once_with(mock_bear, data.non_priority_player)
        assert mock_bear not in game.p1.hand, "Card was played out of a hand but was not removed."
        game.put_action_on_stack.assert_called_once_with(data, "Cast", mock_bear)

    def test_cast_instant_successfully(self, game, mock_bolt):
        """Creature is cast and put on the stack."""
        game.p1.hand = [mock_bolt]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock()
        game.cast_spell(data, mock_bolt)
        game.p1.pay_for_manacost.assert_called_once_with(mock_bolt, data.non_priority_player)
        mock_bolt.ability.can_activate.assert_called_once_with(
            mock_bolt, data.priority_player, data.non_priority_player,
        )
        mock_bolt.ability.pay_cost.assert_called_once_with(
            mock_bolt, data.priority_player, data.non_priority_player,
        )
        assert mock_bolt not in game.p1.hand, "Card was played out of a hand but was not removed."
        game.put_action_on_stack.assert_called_once_with(data, "Cast", mock_bolt)

    def test_cast_sorcery_successfully(self, game, mock_sorcery):
        """Creature is cast and put on the stack."""
        game.p1.hand = [mock_sorcery]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock()
        game.cast_spell(data, mock_sorcery)
        game.p1.pay_for_manacost.assert_called_once_with(mock_sorcery, data.non_priority_player)
        mock_sorcery.ability.can_activate.assert_called_once_with(
            mock_sorcery, data.priority_player, data.non_priority_player,
        )
        mock_sorcery.ability.pay_cost.assert_called_once_with(
            mock_sorcery, data.priority_player, data.non_priority_player,
        )
        assert mock_sorcery not in game.p1.hand, "Card was played out of a hand but was not removed."
        game.put_action_on_stack.assert_called_once_with(data, "Cast", mock_sorcery)

