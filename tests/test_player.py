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
from src.Player.Player import Player, PASS
from src.implementation.cards import get_card


class TestHelper:
    """Test helper methods from Player class"""

    def test_player_moves_creature_from_field_to_grave(self, mock_player, mock_bear):
        """Card disappears from field and appears in the graveyard. Happypath."""
        mock_bear.reset = MagicMock()
        mock_player.creatures = [mock_bear]

        mock_player.send_creature_from_field_to_graveyard(mock_bear)

        assert mock_bear not in mock_player.creatures
        assert mock_bear in mock_player.graveyard
        mock_bear.reset.assert_called_once()

    def test_player_moves_land_from_field_to_grave(self, mock_player, mock_land):
        """Card disappears from field and appears in the graveyard. Happypath."""
        mock_land.reset = MagicMock()
        mock_player.lands = [mock_land]

        mock_player.send_land_from_field_to_graveyard(mock_land)

        assert mock_land not in mock_player.lands
        assert mock_land in mock_player.graveyard
        mock_land.reset.assert_called_once()

    def test_player_discards_a_card_to_graveyard(self, mock_player, mock_bear):
        """Card is removed from hand and is added to the graveyard. Happypath."""
        mock_bear.reset = MagicMock()
        mock_player.hand = [mock_bear]

        mock_player.discard_one_card(mock_bear)

        assert mock_bear not in mock_player.hand
        assert len(mock_player.hand) == 0
        assert mock_bear in mock_player.graveyard


class TestCollectActions:
    """Test player.collect_actions, but logic to call player.collect_landdrops is only really tested."""
    
    def test_playing_land_is_legal(self, game, mock_land):
        """Playing a land is generated as a legal action."""
        game.p1.hand = [mock_land]
        game.hit_landdrop = False

        actions = game.p1.collect_actions(
            sorcery_speed=True, hit_landdrop=game.hit_landdrop, opponent=game.p2
        )

        assert len(actions) == 1
        game.p1.collect_casting_spells.assert_called_once()
        game.p1.collect_landdrops.assert_called_once()
        game.p1.collect_activated_abilities.assert_called_once()

    def test_playing_land_illegal_at_instant_speed(self, game, mock_land):
        """Playing a land is not generated at instant speed."""
        game.p1.hand = [mock_land]
        game.hit_landdrop = False

        actions = game.p1.collect_actions(
            sorcery_speed=False, hit_landdrop=game.hit_landdrop, opponent=game.p2,
        )

        assert len(actions) == 1
        game.p1.collect_landdrops.assert_not_called()
        game.p1.collect_casting_spells.assert_called_once()
        game.p1.collect_activated_abilities.assert_called_once()

    def test_playing_land_illegal_after_landdrop(self, game, mock_land):
        """Playing a land is not generated when landdrop has already happened."""
        game.p1.hand = [mock_land]
        game.hit_landdrop = True

        actions = game.p1.collect_actions(
            sorcery_speed=True, hit_landdrop=game.hit_landdrop, opponent=game.p2,
        )

        assert len(actions) == 1
        game.p1.collect_landdrops.assert_not_called()
        game.p1.collect_casting_spells.assert_called_once()
        game.p1.collect_activated_abilities.assert_called_once()

    def test_playing_land_illegal_at_instant_speed_and_after_landdrop(self, game, mock_land):
        """Playing a land is not generated at instant speed and after a landdrop has happened."""
        game.p1.hand = [mock_land]
        game.hit_landdrop = True

        actions = game.p1.collect_actions(
            sorcery_speed=False, hit_landdrop=game.hit_landdrop, opponent=game.p2,
        )

        assert len(actions) == 1
        game.p1.collect_landdrops.assert_not_called()
        game.p1.collect_casting_spells.assert_called_once()
        game.p1.collect_activated_abilities.assert_called_once()

class TestCollectLanddrops:
    """Test function Player.collect_landdrops"""
        
    def test_landdrop_is_generated_from_hand(self, mock_player, mock_land):
        """Player.collect_landdrops finds the landdrop. Happy-path."""
        mock_player.hand = [mock_land]

        drops = mock_player.collect_landdrops()

        assert len(drops) == 1
        action, land = drops[0]
        assert action == "Play"
        assert land == mock_land

    def test_no_landdrop_is_generated_without_land(self, mock_player, mock_bear, mock_bolt):
        """No landdrop gets generated without a land in hand."""
        mock_player.hand = [mock_bear, mock_bolt]

        drops = mock_player.collect_landdrops()

        assert len(drops) == 0

    def test_only_landdrops_is_generated_in_mixed_hand(self, mock_player, mock_land, mock_bear, mock_bolt):
        """Only the landdrop gets generated in a mixed hand."""
        mock_player.hand = [mock_land, mock_bear, mock_bolt]

        drops = mock_player.collect_landdrops()

        assert len(drops) == 1
        action, land = drops[0]
        assert action == "Play"
        assert land == mock_land

    def test_landdrop_not_generated_from_graveyard(self, mock_player, mock_land):
        """No landdrop gets generated with no land in hand and one in the graveyard."""
        mock_player.hand = []
        mock_player.graveyard = []

        drops = mock_player.collect_landdrops()

        assert len(drops) == 0

class TestCollectCastingSpells:
    """Test function Player.collect_casting_spells"""

    # ARTIFACTS

    def test_collect_casting_artifact_at_sorcery_speed(self, mock_player, mock_artifact):
        """Casting an artifact is collected."""
        mock_player.hand = [mock_artifact]

        casts = mock_player.collect_casting_spells(sorcery_speed=True)

        assert len(casts) == 1
        action, artifact = casts[0]
        assert action == "Cast"
        assert artifact == mock_artifact

    def test_not_collect_casting_artifacts_at_instant_speed(self, mock_player, mock_artifact):
        """Casting the bear is not collected at instant speed."""
        mock_player.hand = [mock_artifact]

        casts = mock_player.collect_casting_spells(sorcery_speed=False)

        assert len(casts) == 0

    # CREATURES

    def test_collect_casting_creature_at_sorcery_speed(self, mock_player, mock_bear):
        """Casting the bear is collected."""
        mock_player.hand = [mock_bear]

        casts = mock_player.collect_casting_spells(sorcery_speed=True)

        assert len(casts) == 1
        action, creature = casts[0]
        assert action == "Cast"
        assert creature == mock_bear

    def test_not_collect_casting_creature_at_instant_speed(self, mock_player, mock_bear):
        """Casting the bear is not collected at instant speed."""
        mock_player.hand = [mock_bear]

        casts = mock_player.collect_casting_spells(sorcery_speed=False)

        assert len(casts) == 0

    # INSTANTS

    def test_collect_casting_instant_at_sorcery_speed(self, mock_player, mock_bolt):
        """Casting the bolt is collected."""
        mock_player.hand = [mock_bolt]

        casts = mock_player.collect_casting_spells(sorcery_speed=True)

        assert len(casts) == 1
        action, instant = casts[0]
        assert action == "Cast"
        assert instant == mock_bolt

    def test_collect_casting_instant_at_instant_speed(self, mock_player, mock_bolt):
        """Casting the bolt is collected."""
        mock_player.hand = [mock_bolt]

        casts = mock_player.collect_casting_spells(sorcery_speed=False)

        assert len(casts) == 1
        action, instant = casts[0]
        assert action == "Cast"
        assert instant == mock_bolt

    # SORCERIES

    def test_collect_casting_sorcery_at_sorcery_speed(self, mock_player, mock_sorcery):
        """Casting the sorcery is collected."""
        mock_player.hand = [mock_sorcery]

        casts = mock_player.collect_casting_spells(sorcery_speed=True)

        assert len(casts) == 1
        action, sorcery = casts[0]
        assert action == "Cast"
        assert sorcery == mock_sorcery

    def test_not_collect_casting_sorcery_at_instant_speed(self, mock_player, mock_sorcery):
        """Casting the sorcery is not collected at instant speed."""
        mock_player.hand = [mock_sorcery]

        casts = mock_player.collect_casting_spells(sorcery_speed=False)

        assert len(casts) == 0

    # NOT LANDS

    def test_no_landdrop_is_collected_at_sorcery_speed(self, mock_player, mock_land):
        """Landdrops are not collected at sorcery speed."""
        mock_player.hand = [mock_land]

        casts = mock_player.collect_casting_spells(sorcery_speed=True)

        assert len(casts) == 0

    def test_no_landdrop_is_collected_at_instant_speed(self, mock_player, mock_land):
        """Landdrops are not collected at instant speed."""
        mock_player.hand = [mock_land]

        casts = mock_player.collect_casting_spells(sorcery_speed=False)

        assert len(casts) == 0

    # MIXED

    def test_creature_instant_sorcery_are_collected_at_sorcery_speed(
        self, mock_player, mock_bear, mock_bolt, mock_sorcery, mock_land
    ):
        """All but the land are collected as casts at sorcery speed."""
        mock_player.hand = [mock_bear, mock_bolt, mock_sorcery, mock_land]

        casts = mock_player.collect_casting_spells(sorcery_speed=True)

        for action, card in casts:
            assert action == "Cast"
            assert isinstance(card, Spell)
            assert card in [mock_bear, mock_bolt, mock_sorcery]

    def test_only_instant_is_collected_at_sorcery_speed(
        self, mock_player, mock_bear, mock_bolt, mock_sorcery, mock_land
    ):
        """Only the instant spell is collected as casts at instant speed."""
        mock_player.hand = [mock_bear, mock_bolt, mock_sorcery, mock_land]

        casts = mock_player.collect_casting_spells(sorcery_speed=False)

        for action, card in casts:
            assert action == "Cast"
            assert isinstance(card, Spell)
            assert not card.sorcery_speed
            assert card == mock_bolt

class TestCollectActivatedAbilities:
    """Test function player.collect_activated_abilities"""

    # CAN ACTIVATE - HAPPY PATH

    def test_collect_ability_from_artifact_on_board(self, mock_player, mock_artifact):
        """Artifact is on the field and its non-mana-ability is collected."""
        mock_player.nc_permanents = [mock_artifact]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_artifact

    def test_collect_ability_from_creature_on_board(self, mock_player, mock_bear):
        """Creature is on the field and its non-mana-ability is collected."""
        mock_player.creatures = [mock_bear]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_bear

    def test_collect_ability_from_land_on_board(self, mock_player, mock_land):
        """Land is on the field and its non-mana-ability is collected."""
        mock_land.activated_ability.is_mana_ability = False
        mock_player.lands = [mock_land]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_land

    # CANNOT ACTIVATE

    def test_not_collect_ability_from_creature_on_board_cannot_activate(self, mock_player, mock_artifact):
        """Artifact is on the field and its non-mana-ability is not collected."""
        mock_artifact.activated_ability.can_activate = MagicMock(return_value=False)
        mock_player.nc_permanents = [mock_artifact]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 0

    def test_not_collect_ability_from_creature_on_board_cannot_activate(self, mock_player, mock_bear):
        """Creature is on the field and its non-mana-ability is not collected."""
        mock_bear.activated_ability.can_activate = MagicMock(return_value=False)
        mock_player.creatures = [mock_bear]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 0

    def test_not_collect_ability_from_land_on_board_cannot_activate(self, mock_player, mock_land):
        """Land is on the field and its non-mana-ability is not collected."""
        mock_land.activated_ability.is_mana_ability = False
        mock_land.activated_ability.can_activate = MagicMock(return_value=False)
        mock_player.lands = [mock_land]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 0

    # SKIP MANA ABILITIES

    def test_not_collect_mana_ability_from_artifact_on_board(self, mock_player, mock_artifact):
        """Artifact is on the field and its mana-ability is not collected."""
        mock_artifact.activated_ability.is_mana_ability = True
        mock_player.nc_permanents = [mock_artifact]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 0

    def test_not_collect_mana_ability_from_creature_on_board(self, mock_player, mock_bear):
        """Creature is on the field and its mana-ability is not collected."""
        mock_bear.activated_ability.is_mana_ability = True
        mock_player.creatures = [mock_bear]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 0

    def test_not_collect_mana_ability_from_land_on_board(self, mock_player, mock_land):
        """Land is on the field and its mana-ability is not collected."""
        mock_player.lands = [mock_land]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 0

    # CAN ACTIVATE FROM HAND

    def test_collect_ability_from_artifact_in_hand(self, mock_player, mock_artifact):
        """Creature is in owners hand and its non-mana-ability is collected."""
        mock_player.hand = [mock_artifact]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_artifact

    def test_collect_ability_from_creature_in_hand(self, mock_player, mock_bear):
        """Creature is in owners hand and its non-mana-ability is collected."""
        mock_player.hand = [mock_bear]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_bear

    def test_collect_ability_from_land_in_hand(self, mock_player, mock_land):
        """Land is in its owners hand and its non-mana-ability is collected."""
        mock_land.activated_ability.is_mana_ability = False
        mock_player.hand = [mock_land]

        abilities = mock_player.collect_activated_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_land


class TestCollectManaAbilities:
    """Test player.collect_mana_abilities"""

    # CAN ACTIVATE

    def test_collect_mana_ability_from_artifact_on_board(self, mock_player, mock_artifact):
        """Artifact is on the field and its mana-ability is collected."""
        mock_artifact.activated_ability.is_mana_ability = True
        mock_player.nc_permanents = [mock_artifact]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_artifact
        mock_artifact.activated_ability.can_activate.assert_called_once_with(
            mock_artifact, mock_player, None,
        )

    def test_collect_mana_ability_from_creature_on_board(self, mock_player, mock_bear):
        """Creature is on the field and its mana-ability is collected."""
        mock_bear.activated_ability.is_mana_ability = True
        mock_player.creatures = [mock_bear]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_bear
        mock_bear.activated_ability.can_activate.assert_called_once_with(
            mock_bear, mock_player, None,
        )

    def test_collect_mana_ability_from_land_on_board(self, mock_player, mock_land):
        """Land is on the field and its mana-ability is collected."""
        mock_player.lands = [mock_land]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_land
        mock_land.activated_ability.can_activate.assert_called_once_with(
            mock_land, mock_player, None,
        )

    # CANNOT ACTIVATE

    def test_not_collect_mana_ability_from_creature_on_board_cannot_activate(self, mock_player, mock_artifact):
        """Artifact is on the field and its non-mana-ability is not collected."""
        mock_artifact.activated_ability.is_mana_ability = True
        mock_artifact.activated_ability.can_activate = MagicMock(return_value=False)
        mock_player.nc_permanents = [mock_artifact]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 0

    def test_not_collect_mana_ability_from_creature_on_board_cannot_activate(self, mock_player, mock_bear):
        """Creature is on the field and its non-mana-ability is not collected."""
        mock_bear.activated_ability.is_mana_ability = True
        mock_bear.activated_ability.can_activate = MagicMock(return_value=False)
        mock_player.creatures = [mock_bear]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 0

    def test_not_collect_mana_ability_from_land_on_board_cannot_activate(self, mock_player, mock_land):
        """Land is on the field and its non-mana-ability is not collected."""
        mock_land.activated_ability.can_activate = MagicMock(return_value=False)
        mock_player.lands = [mock_land]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 0

    # NON MANA ABILITIES

    def test_not_collect_ability_from_creature_on_board(self, mock_player, mock_artifact):
        """Artifact is on the field and its non-mana-ability is not collected."""
        mock_artifact.activated_ability.is_mana_ability = False
        mock_player.nc_permanents = [mock_artifact]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 0

    def test_not_collect_ability_from_creature_on_board(self, mock_player, mock_bear):
        """Creature is on the field and its non-mana-ability is not collected."""
        mock_bear.activated_ability.is_mana_ability = False
        mock_player.creatures = [mock_bear]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 0

    def test_not_collect_ability_from_land_on_board(self, mock_player, mock_land):
        """Land is on the field and its non-mana-ability is not collected."""
        mock_land.activated_ability.is_mana_ability = False
        mock_player.lands = [mock_land]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 0

    def test_collect_mana_ability_from_creature_in_hand(self, mock_player, mock_bear):
        """Creature is in owners hand and its mana-ability is collected."""
        mock_bear.activated_ability.is_mana_ability = True
        mock_bear.activated_ability.can_activate = MagicMock(return_value=True)
        mock_player.hand = [mock_bear]

        abilities = mock_player.collect_mana_abilities()

        assert len(abilities) == 1
        action, source = abilities[0]
        assert action == "Ability"
        assert source == mock_bear
        mock_bear.activated_ability.can_activate.assert_called_once_with(
            mock_bear, mock_player, None,
        )
