import sys
import pytest
from unittest.mock import MagicMock, Mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.Magic.Game import Game
from src.Magic.Library import load_from_decklist
from src.Magic.Card import Card, Land, Artifact, Spell, Creature, Instant, Sorcery
from src.Magic.Stack import PriorityData
from src.Magic.Ability import Ability, TriggeredAbility
from src.Magic.Stack import StackObject
from src.Magic.Cost import Cost
from src.Player.Player import Player
from src.implementation.cards import get_card

# Mock(side_effect=[("Cast", card), ("Pass", None)]) -> mock player.choose_action chains


@pytest.fixture
def mock_player() -> Player:
    """Create minimal instance of a Player."""
    return Player("P", 20, [], Mock())

@pytest.fixture
def mock_player_factory():
    """Factory to create minimal instances of a Player."""
    def _mock_player(name: str) -> Player:
        """Create minimal instance of a Player."""
        p = Player(name, 20, [], Mock())
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
def mock_cost() -> Cost:
    """Mock a cost."""
    return Cost(
        mana_cost={},
        has_extra_cost=False,
        can_pay_extra_cost=MagicMock(return_value=True),
        pay_extra_cost=MagicMock(),
    )

@pytest.fixture
def mock_mana_ability() -> Ability:
    """Mock a mana ability."""
    a = Ability(is_mana_ability=True)
    a.can_activate = MagicMock(return_value=True)
    a.choose_targets = MagicMock(return_vaue=[])
    a.pay_cost = MagicMock()
    a.activity = MagicMock()
    return a

@pytest.fixture
def mock_ability() -> Ability:
    """Mock a non-mana ability."""
    a = Ability(is_mana_ability=False)
    a.can_activate = MagicMock(return_value=True)
    a.choose_targets = MagicMock(return_value=[])
    a.pay_cost = MagicMock()
    a.activity = MagicMock()
    return a

@pytest.fixture
def mock_triggered_ability() -> TriggeredAbility:
    """Mock a triggered ability."""
    a = TriggeredAbility()
    a.can_activate = MagicMock(return_value=True)
    a.activity = MagicMock()
    return a

@pytest.fixture
def mock_land() -> Land:
    """Mock a land Card."""
    land = get_card("Forest")
    land.name = "Mock_Land"
    land.activated_ability = Ability(is_mana_ability=True)
    land.activated_ability.can_activate = MagicMock(return_value=True)
    land.activated_ability.choose_targets=MagicMock(return_value=[])
    land.activated_ability.pay_cost=MagicMock()
    land.activated_ability.activity=MagicMock()
    return land

@pytest.fixture
def mock_artifact(mock_cost) -> Artifact:
    """Mock an artifact."""
    artifact = get_card("Springleaf_Drum")
    artifact.cost = mock_cost
    artifact.activated_ability = MagicMock()
    artifact.activated_ability.is_mana_ability = False
    return artifact

@pytest.fixture
def mock_trample_dino(mock_cost) -> Creature:
    """Mock a trampling Dino."""
    creature = get_card("Colossal_Dreadmaw")
    creature.cost = mock_cost
    creature.name = "Mock_Dino"
    creature.summoning_sick = False
    return creature

@pytest.fixture
def mock_flying_birb(mock_cost) -> Creature:
    """Mock a flying Bird."""
    birb = get_card("Storm_Crow")
    birb.cost = mock_cost
    birb.name = "Mock Birb"
    birb.summoning_sickness = False
    return birb

@pytest.fixture
def mock_bear(mock_ability, mock_cost) -> Creature:
    """Mock a vanilla creature."""
    bear = get_card("Balduvian_Bears")
    bear.name = "Mock_reature"
    bear.summoning_sick = False
    bear.activated_ability = mock_ability
    bear.cost = mock_cost
    return bear

@pytest.fixture
def mock_bear_factory():
    def _mock_bear() -> Creature:
        """Mock a vanilla creature."""
        creature = get_card("Balduvian_Bears")
        creature.name = "Mock_creature"
        creature.summoning_sick = False
        creature.activated_ability = MagicMock()
        creature.mock_cost = MagicMock()
        return creature
    return _mock_bear

@pytest.fixture
def mock_elf_dork(mock_mana_ability, mock_cost):
    """Mock Elf that taps for {G}."""
    elf = get_card("Llanowar Elves")
    elf.name = "Mock Elf Dork"
    elf.summoning_sick = False
    elf.activated_ability = mock_mana_ability
    elf.cost = mock_cost
    return elf

@pytest.fixture
def mock_elf_dork_factory():
    def _mock_elf_dork():
        """Mock Elf that taps for {G}."""
        creature = get_card("Llanowar_Elves")
        creature.name = "Mock Elf Dork"
        creature.summoning_sick = False
        creature.activated_ability = MagicMock()
        creature.cost = MagicMock()
        return creature
    return _mock_elf_dork

@pytest.fixture
def mock_bolt(mock_ability, mock_cost) -> Instant:
    """Mock an instant spell."""
    bolt: Instant = get_card("Lightning_Bolt")
    bolt.name = "Mock_Instant"
    bolt.ability = mock_ability
    bolt.cost = mock_cost
    return bolt

@pytest.fixture
def mock_sorcery(mock_ability, mock_cost) -> Instant:
    """Mock an instant spell."""
    sorcery: Instant = get_card("Horrific_Assault")
    sorcery.name = "Mock_Sorcery"
    sorcery.ability = mock_ability
    sorcery.cost = mock_cost
    return sorcery

def build_priority_data(game: Game, pass_counter=0) -> PriorityData:
    """Build minimal priority data object."""
    return PriorityData(
        state="Action",
        priority_player=game.p1,
        non_priority_player=game.p2,
        pass_counter=pass_counter,
    )