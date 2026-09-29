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
from src.Magic.Stack import StackObject
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


class TestHelperMethods:

    # PLAYING LANDS
    
    def test_play_land_happypath(self, game, mock_land):   
        """Playing a land makes the landdrop correctly."""
        data = build_priority_data(game)
        game.p1.hand = [mock_land]
        game.put_action_on_stack = MagicMock()

        game.play_land(data, mock_land)

        assert mock_land not in game.p1.hand, "Land Should have been removed from Hand."
        assert mock_land in game.p1.lands, "Land should have appeard on the Field."
        assert game.hit_landdrop, "Landdrop has been made."
        game.put_action_on_stack.assert_not_called()

    # ACTIVATING MANA ABILITIES

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

    # ACTIVATING ABILITIES

    def test_activate_ability_can_activate(self, game, mock_bear):
        """Activating an ability puts it on the stack."""
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=True)

        game.activate_ability(data, mock_bear)

        mock_bear.activated_ability.can_activate.assert_called_once_with(
            mock_bear, data.priority_player, data.non_priority_player,
        )
        mock_bear.activated_ability.choose_targets.assert_called_once_with(
            mock_bear, data.priority_player, data.non_priority_player,
        )
        data.priority_player.pay_for_manacost.assert_not_called()
        mock_bear.activated_ability.pay_cost.assert_called_once_with(
            mock_bear, data.priority_player, data.non_priority_player,
        )
        mock_bear.activated_ability.activity.assert_not_called()
        game.put_action_on_stack.assert_called_once_with(
            data, "Ability", mock_bear,
        )

    def test_activate_ability_can_not_activate(self, game, mock_bear):
        """Ability can not activate and is not put on the stack."""
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=True)
        mock_bear.activated_ability.can_activate = MagicMock(return_value=False)

        game.activate_ability(data, mock_bear)

        mock_bear.activated_ability.can_activate.assert_called_once_with(
            mock_bear, data.priority_player, data.non_priority_player,
        )
        mock_bear.activated_ability.choose_targets.assert_not_called()
        data.priority_player.pay_for_manacost.assert_not_called()
        mock_bear.activated_ability.pay_cost.assert_not_called()
        mock_bear.activated_ability.activity.assert_not_called()
        game.put_action_on_stack.assert_not_called()


    # CASTING CREATURES

    def test_cast_creature_successfully(self, game, mock_bear):
        """Creature is cast and put on the stack."""
        game.p1.hand = [mock_bear]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=True)

        game.cast_spell(data, mock_bear)

        game.p1.pay_for_manacost.assert_called_once_with(mock_bear.cost, data.non_priority_player)
        assert mock_bear not in game.p1.hand, "Card was played, it should leave the hand."
        assert mock_bear not in game.p1.creatures, "Card was played, it should be on the stack."
        game.put_action_on_stack.assert_called_once_with(data, "Cast", mock_bear)

    def text_cast_creature_not_enough_mana(self, game, mock_bear):
        """Casting creature is attempted and failed."""
        game.p1.hand = [mock_bear]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=False)
        game.cast_spell(data, mock_bear)
        game.p1.pay_for_manacost.assert_called_once_with(mock_bear.cost, data.non_priority_player)
        assert mock_bear in game.p1.hand, "Card was not played, it should stay in hand."
        assert mock_bear not in game.p1.creatures, "Card was not played, should not etb."
        game.put_action_on_stack.assert_called_once_with(data, "Cast", mock_bear)


    # CASTING INSTANTS

    def test_cast_instant_successfully(self, game, mock_bolt):
        """Instant is cast and put on the stack."""
        game.p1.hand = [mock_bolt]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=True)

        game.cast_spell(data, mock_bolt)
        
        mock_bolt.ability.can_activate.assert_called_once_with(
            mock_bolt, data.priority_player, data.non_priority_player,
        )
        mock_bolt.ability.choose_targets.assert_called_once_with(
            mock_bolt, data.priority_player, data.non_priority_player,
        )
        game.p1.pay_for_manacost.assert_called_once_with(
            mock_bolt.cost, data.non_priority_player
        )      
        mock_bolt.ability.pay_cost.assert_called_once_with(
            mock_bolt, data.priority_player, data.non_priority_player,
        )
        assert mock_bolt not in game.p1.hand, "Card was played, it should leave the hand."
        assert mock_bolt not in game.p1.graveyard, "Card was played, it should be on the stack."
        game.put_action_on_stack.assert_called_once_with(data, "Cast", mock_bolt)

    def test_cast_instant_cannot_pay_mana(self, game, mock_bolt):
        """Instant mana cost cannot be payed and it is not cast."""
        game.p1.hand = [mock_bolt]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=False)

        game.cast_spell(data, mock_bolt)

        mock_bolt.ability.can_activate.assert_called_once_with(
            mock_bolt, data.priority_player, data.non_priority_player,
        )
        mock_bolt.ability.choose_targets.assert_called_once_with(
            mock_bolt, data.priority_player, data.non_priority_player,
        )
        game.p1.pay_for_manacost.assert_called_once_with(
            mock_bolt.cost, data.non_priority_player
        )      
        mock_bolt.ability.pay_cost.assert_not_called()
        assert mock_bolt in game.p1.hand, "Card was not played, it should stay in hand."
        assert mock_bolt not in game.p1.graveyard, "Card was not played, it should not be on stack."
        game.put_action_on_stack.assert_not_called()

    def test_cast_instant_ability_cannot_activate(self, game, mock_bolt):
        """Instant ability cannot activate and it is not cast."""
        game.p1.hand = [mock_bolt]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=True)
        mock_bolt.ability.can_activate = MagicMock(return_value=False)

        game.cast_spell(data, mock_bolt)

        mock_bolt.ability.can_activate.assert_called_once_with(
            mock_bolt, data.priority_player, data.non_priority_player,
        )
        mock_bolt.ability.choose_targets.assert_not_called()
        game.p1.pay_for_manacost.assert_not_called()
        mock_bolt.ability.pay_cost.assert_not_called()
        assert mock_bolt in game.p1.hand, "Card was not played, it should stay in hand."
        assert mock_bolt not in game.p1.graveyard, "Card was not played, it should not be on stack."
        game.put_action_on_stack.assert_not_called()


    # CASTING SORCERIES

    def test_cast_sorcery_successfully(self, game, mock_sorcery):
        """Sorcery is cast and put on the stack."""
        game.p1.hand = [mock_sorcery]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=True)

        game.cast_spell(data, mock_sorcery)
        
        mock_sorcery.ability.can_activate.assert_called_once_with(
            mock_sorcery, data.priority_player, data.non_priority_player,
        )
        mock_sorcery.ability.choose_targets.assert_called_once_with(
            mock_sorcery, data.priority_player, data.non_priority_player,
        )
        game.p1.pay_for_manacost.assert_called_once_with(
            mock_sorcery.cost, data.non_priority_player
        )      
        mock_sorcery.ability.pay_cost.assert_called_once_with(
            mock_sorcery, data.priority_player, data.non_priority_player,
        )
        assert mock_sorcery not in game.p1.hand, "Card was played, it should leave the hand."
        assert mock_sorcery not in game.p1.graveyard, "Card was played, it should be on the stack."
        game.put_action_on_stack.assert_called_once_with(data, "Cast", mock_sorcery)

    def test_cast_sorcery_cannot_pay_mana(self, game, mock_sorcery):
        """Sorcery mana cost cannot be payed and it is not cast."""
        game.p1.hand = [mock_sorcery]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=False)

        game.cast_spell(data, mock_sorcery)

        mock_sorcery.ability.can_activate.assert_called_once_with(
            mock_sorcery, data.priority_player, data.non_priority_player,
        )
        mock_sorcery.ability.choose_targets.assert_called_once_with(
            mock_sorcery, data.priority_player, data.non_priority_player,
        )
        game.p1.pay_for_manacost.assert_called_once_with(
            mock_sorcery.cost, data.non_priority_player
        )      
        mock_sorcery.ability.pay_cost.assert_not_called()
        assert mock_sorcery in game.p1.hand, "Card was not played, it should stay in hand."
        assert mock_sorcery not in game.p1.graveyard, "Card was not played, it should not be on stack."
        game.put_action_on_stack.assert_not_called()

    def test_cast_sorcery_ability_cannot_activate(self, game, mock_sorcery):
        """Sorcery ability cannot activate and it is not cast."""
        game.p1.hand = [mock_sorcery]
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=True)
        mock_sorcery.ability.can_activate = MagicMock(return_value=False)

        game.cast_spell(data, mock_sorcery)

        mock_sorcery.ability.can_activate.assert_called_once_with(
            mock_sorcery, data.priority_player, data.non_priority_player,
        )
        mock_sorcery.ability.choose_targets.assert_not_called()
        game.p1.pay_for_manacost.assert_not_called()
        mock_sorcery.ability.pay_cost.assert_not_called()
        assert mock_sorcery in game.p1.hand, "Card was not played, it should stay in hand."
        assert mock_sorcery not in game.p1.graveyard, "Card was not played, it should not be on stack."
        game.put_action_on_stack.assert_not_called()


    # PASSING

    def test_first_pass_swaps_priority(self, game):
        """After first pass, the opponent receives priority."""
        data = build_priority_data(game, pass_counter=1)
        data.swap_priority = MagicMock()
        game.swap_priority(data)
        data.swap_priority.assert_called_once()
        assert data.state == "Action"

    def test_second_pass_resolves_the_stack(self, game):
        """After a second pass in a row the stack resolves."""
        data = build_priority_data(game, pass_counter=2)
        data.swap_priority = MagicMock()
        game.swap_priority(data)
        data.swap_priority.assert_not_called()
        assert data.state == "Resolve"
    

    # RESOLVING THE STACK
    
    def test_resolve_creature_from_stack(self, game, mock_bear):
        """Happy path for resolving a creature from the stack."""
        game.stack = [
            StackObject(action="Cast", source=mock_bear, owner=game.p1)
        ]
        game.state_based_actions = MagicMock()
        data: PriorityData = MagicMock()
        game.resolve_top_object_from_stack(data)
        assert len(game.stack) == 0
        assert mock_bear in game.p1.creatures
        game.state_based_actions.assert_called_once()

    def test_resolve_instant_from_stack(self, game, mock_bolt):
        """Happy path for resolving an instant from the stack."""
        game.stack = [
            StackObject(action="Cast", source=mock_bolt, owner=game.p1)
        ]
        game.state_based_actions = MagicMock()
        data: PriorityData = MagicMock()
        game.resolve_top_object_from_stack(data)
        assert len(game.stack) == 0
        assert mock_bolt in game.p1.graveyard
        game.state_based_actions.assert_called_once()
