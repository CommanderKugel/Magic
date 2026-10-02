import sys
import pytest
from unittest.mock import MagicMock, Mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.Magic.Game import Game
from src.Magic.Library import load_from_decklist
from src.Magic.Card import Card, Land, Spell, Creature, Instant, Sorcery
from src.Magic.Stack import PriorityData
from src.Magic.Ability import Ability
from src.Magic.Stack import StackObject
from src.Player.Player import Player
from src.implementation.cards import get_card

# Mock(side_effect=[("Cast", card), ("Pass", None)]) -> mock player.choose_action chains


@pytest.fixture
def mock_player() -> Player:
    """Create minimal instance of a Player."""
    return Player("P", 20, [])

@pytest.fixture
def mock_player_factory():
    """Factory to create minimal instances of a Player."""
    def _mock_player(name: str) -> Player:
        """Create minimal instance of a Player."""
        p = Player(name, 20, [])
        p.collect_casting_spells = MagicMock(return_value=[])
        p.collect_activated_abilities = MagicMock(return_value=[])
        p.collect_landdrops = MagicMock(return_value=[])
        return p
    return _mock_player

@pytest.fixture
def game(mock_player_factory) -> Game:
    """Create minimal instance of game object. ATTENTION: players decks are empty!"""
    g = Game(
        p1=mock_player_factory(name="P1"),
        p2=mock_player_factory(name="P2"),
    )
    g.active_player = g.p1
    g.reactive_player = g.p2
    return g

@pytest.fixture
def mock_mana_ability() -> Ability:
    """Mock a mana ability."""
    a = Ability(is_mana_ability=True)
    a.can_activate = MagicMock(return_value=True)
    a.choose_targets = MagicMock()
    a.pay_cost = MagicMock()
    a.activity = MagicMock()
    return a

@pytest.fixture
def mock_ability() -> Ability:
    """Mock a non-mana ability."""
    a = Ability(is_mana_ability=False)
    a.can_activate = MagicMock(return_value=True)
    a.choose_targets = MagicMock()
    a.pay_cost = MagicMock()
    a.activity = MagicMock()
    return a

@pytest.fixture
def mock_land() -> Land:
    """Mock a land Card."""
    land = get_card("Forest")
    land.name = "Mock_Land"
    land.activated_ability = Ability(is_mana_ability=True)
    land.activated_ability.can_activate = MagicMock(return_value=True)
    land.activated_ability.choose_targets=MagicMock()
    land.activated_ability.pay_cost=MagicMock()
    land.activated_ability.activity=MagicMock()
    return land

@pytest.fixture
def mock_bear(mock_ability) -> Creature:
    """Mock a vanilla creature."""
    creature = get_card("Balduvian_Bears")
    creature.name = "Mock_reature"
    creature.activated_ability = mock_ability
    return creature

@pytest.fixture
def mock_bear_factory():
    def _mock_bear() -> Creature:
        """Mock a vanilla creature."""
        creature = get_card("Balduvian_Bears")
        creature.name = "Mock_reature"
        creature.activated_ability = MagicMock()
        return creature
    return _mock_bear

@pytest.fixture
def mock_bolt(mock_ability) -> Instant:
    """Mock an instant spell."""
    instant: Instant = get_card("Lightning_Bolt")
    instant.name = "Mock_Instant"
    instant.ability = mock_ability
    return instant

@pytest.fixture
def mock_sorcery(mock_ability) -> Instant:
    """Mock an instant spell."""
    sorcery: Instant = get_card("Horrific_Assault")
    sorcery.name = "Mock_Sorcery"
    sorcery.ability = mock_ability
    return sorcery

def build_priority_data(game: Game, pass_counter=0) -> PriorityData:
    """Build minimal priority data object."""
    return PriorityData(
        state="Action",
        priority_player=game.p1,
        non_priority_player=game.p2,
        pass_counter=pass_counter,
    )