import sys
import pytest
import random
from unittest.mock import MagicMock, Mock
from pathlib import Path

from conftest import build_priority_data

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.Magic.Game import Game
from src.Magic.Modifier import Modifier, Buff
from src.Magic.Library import load_from_decklist
from src.Magic.Card import Card, Land, Spell, Creature, Instant, Sorcery
from src.Magic.Stack import PriorityData
from src.Magic.Ability import Ability
from src.Magic.Stack import StackObject
from src.Player.Player import Player
from src.implementation.cards import get_card


class TestBeginningPhase:
    """Test simulating the beginning phase. Including untap-, upkeep- & draw-step."""

    def test_untap_step_untapps_creatures(self, game, mock_bear):
        """All creatures should be untapped after untap step."""
        mock_bear.tapped = True
        game.p1.creatures = [mock_bear]
        game.priority = MagicMock()

        game.untap_step()

        assert mock_bear in game.p1.creatures
        assert not mock_bear.tapped
        game.priority.assert_not_called()

    def test_untap_step_removes_summoning_sickness(self, game, mock_bear):
        """All creatures loose summoning sickness."""
        mock_bear.summoning_sick = True
        game.p1.creatures = [mock_bear]
        game.priority = MagicMock()

        game.untap_step()

        assert not mock_bear.summoning_sick
        game.priority.assert_not_called()

    def test_untap_step_untapps_lands(self, game, mock_land):
        """All lands should be untapped after untap step."""
        mock_land.tapped = True
        game.p1.lands = [mock_land]
        game.priority = MagicMock()

        game.untap_step()

        assert mock_land in game.p1.lands
        assert not mock_land.tapped
        game.priority.assert_not_called()

    # TODO: skip permanents that dont untap during the upkeep

    def test_upkeep_uses_prioroty(self, game):
        """Priority is played at instant speed during upkeep."""
        game.priority = MagicMock()

        game.upkeep_step()

        game.priority.assert_called_once_with(sorcery_speed=False)

    # TODO: upkeep step triggers abilities

    def test_draw_step_draws_a_card(self, game):
        """One card is drawn during upkeep."""
        game.p1.draw = MagicMock()
        game.priority = MagicMock()

        game.draw_step()

        game.p1.draw.assert_called_once_with(1)
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_beginning_phase_has_all_steps(self, game):
        """There should be untap, upkeep and draw."""
        game.untap_step = MagicMock()
        game.upkeep_step = MagicMock()
        game.draw_step = MagicMock()

        game.beginning_phase()

        game.untap_step.assert_called_once()
        game.upkeep_step.assert_called_once()
        game.draw_step.assert_called_once()


class TestMainPhase:
    """Test simulating the main phase."""

    def test_main_phase_has_prio_at_sorcery_speed(self, game):
        """In the main phase priority is gained at sorcery speed."""
        game.priority = MagicMock()
        game.clear_player_mana = MagicMock()

        game.main_phase()

        game.priority.assert_called_once_with(sorcery_speed=True)


class TestCombatPhase:
    """Test simulating the combat phase."""

    # BEGINNING OF COMBAT

    def test_beginning_of_combat_has_instant_speed_priority(self, game):
        """Beginning of combat has one round of priority."""
        game.priority = MagicMock()

        game.beginning_of_combat_step()

        game.priority.assert_called_once_with(sorcery_speed=False)

    # HELPER: CAN ATTACK

    def test_creature_can_attack(self, game, mock_bear):
        """Creature can attack. Happypath."""
        game.p1.creatures = [mock_bear]

        can_attack = game.can_attack(mock_bear, game.p1)

        assert can_attack

    def test_tapped_creature_cannot_attack(self, game, mock_bear):
        """Tapped creatures can not attack."""
        mock_bear.tapped = True
        game.p1.creatures = [mock_bear]

        can_attack = game.can_attack(mock_bear, game.p1)

        assert not can_attack

    def test_summoningsick_creature_cannot_attack(self, game, mock_bear):
        """Tapped creatures can not attack."""
        mock_bear.summoning_sick = True
        game.p1.creatures = [mock_bear]

        can_attack = game.can_attack(mock_bear, game.p1)

        assert not can_attack

    # HELPER: CAN BLOCK

    def test_creature_can_block_attacker(self, game, mock_bear):
        """Creature can block attacker. Happypath."""
        game.p1.creatures = [mock_bear]
        mock_bear.tapped = False

        can_block = game.can_block(mock_bear, game.p2)

        assert can_block

    def test_tapped_creature_can_not_block(self, game, mock_bear):
        """Tapped creature can not block attacker."""
        game.p1.creatures = [mock_bear]
        mock_bear.tapped = True

        can_block = game.can_block(mock_bear, game.p2)

        assert not can_block


    # HELPER: CAN BE BLOCKED

    def test_creature_can_block_attacker(self, game, mock_bear_factory):
        """Bear is allowed to block a bear. Vanilly Happypath."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        game.p1.creatures = [bear_1]
        game.p2.creatures = [bear_2]
        bear_1.tapped = True

        allowed_to_block = game.can_be_blocked(bear_1, bear_2)

        assert allowed_to_block

    def test_flyer_cannot_be_blocked_by_bear(self, game, mock_flying_birb, mock_bear):
        """Bear is allowed to block a bear. Vanilly Happypath."""
        allowed_to_block = game.can_be_blocked(mock_flying_birb, mock_bear)
        assert not allowed_to_block

    def test_flyer_can_be_blocked_by_flyer(self, game, mock_flying_birb, mock_bear):
        """Bear is allowed to block a bear. Vanilly Happypath."""
        mock_bear.is_flying = MagicMock(return_value=True)
        allowed_to_block = game.can_be_blocked(mock_flying_birb, mock_bear)
        assert allowed_to_block

    def test_flyer_can_be_blocked_by_reach(self, game, mock_flying_birb, mock_bear):
        """Bear is allowed to block a bear. Vanilly Happypath."""
        mock_bear.has_reach = MagicMock(return_value=True)
        allowed_to_block = game.can_be_blocked(mock_flying_birb, mock_bear)
        assert allowed_to_block

    # DECLARE ATTACKER

    def test_declare_creature_can_and_should_attack(self, game, mock_bear):
        """Attacker is declared successfully. Happypath."""
        game.p1.creatures = [mock_bear]
        game.can_attack = MagicMock(return_value=True)
        game.wants_to_attack = MagicMock(return_value=True)
        game.priority = MagicMock()

        attacker = game.declare_attacker_step()

        game.can_attack.assert_called_once_with(mock_bear, game.p1)
        game.wants_to_attack.assert_called_once_with(mock_bear, game.p1)
        assert len(attacker) == 1
        creature = list(attacker.keys())[0]
        assert creature == mock_bear
        assert creature.tapped
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_declare_creature_can_but_should_not_attack(self, game, mock_bear):
        """Attacker is not declared successfully."""
        game.p1.creatures = [mock_bear]
        game.can_attack = MagicMock(return_value=True)
        game.wants_to_attack = MagicMock(return_value=False)
        game.priority = MagicMock()

        attacker = game.declare_attacker_step()

        game.can_attack.assert_called_once_with(mock_bear, game.p1)
        game.wants_to_attack.assert_called_once_with(mock_bear, game.p1)
        assert len(attacker) == 0
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_declare_creature_can_not_but_should_attack(self, game, mock_bear):
        """Attacker is not declared successfully."""
        game.p1.creatures = [mock_bear]
        game.can_attack = MagicMock(return_value=False)
        game.wants_to_attack = MagicMock(return_value=True)
        game.priority = MagicMock()

        attacker = game.declare_attacker_step()

        game.can_attack.assert_called_once_with(mock_bear, game.p1)
        game.wants_to_attack.assert_not_called()
        assert len(attacker) == 0
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_one_creature_should_and_one_should_not_attack(self, game, mock_bear_factory):
        """Only one attacker is declared successfully."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        game.p1.creatures = [bear_1, bear_2]
        game.can_attack = MagicMock(return_value=True)
        game.wants_to_attack = MagicMock(side_effect=[True, False])
        game.priority = MagicMock()

        attacker = game.declare_attacker_step()

        game.can_attack.assert_any_call(bear_1, game.p1)
        game.can_attack.assert_any_call(bear_2, game.p1)
        game.wants_to_attack.assert_any_call(bear_1, game.p1)
        game.wants_to_attack.assert_any_call(bear_2, game.p1)
        assert len(attacker) == 1
        creature = list(attacker.keys())[0]
        assert creature == bear_1
        assert creature.tapped
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_two_creatures_should_but_one_can_attack(self, game, mock_bear_factory):
        """Only one attacker is declared successfully."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        game.p1.creatures = [bear_1, bear_2]
        game.can_attack = MagicMock(side_effect=[True, False])
        game.wants_to_attack = MagicMock(return_value=True)
        game.priority = MagicMock()

        attacker = game.declare_attacker_step()

        game.can_attack.assert_any_call(bear_1, game.p1)
        game.can_attack.assert_any_call(bear_2, game.p1)
        game.wants_to_attack.assert_called_once_with(bear_1, game.p1)
        assert len(attacker) == 1
        creature = list(attacker.keys())[0]
        assert creature == bear_1
        assert creature.tapped
        game.priority.assert_called_once_with(sorcery_speed=False)

    # DECLARE BLOCKER

    def test_creature_blocks(self, game, mock_bear_factory):
        """One creature can block another creature. Happypath."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        bear_1.tapped = True # attacker
        game.p1.creatures = [bear_1]
        game.p2.creatures = [bear_2]
        game.p2.binary_choice = MagicMock(return_value=True)
        game.can_block = MagicMock(return_value=True)
        game.can_be_blocked = MagicMock(return_value=True)
        game.priority = MagicMock()

        attacker = {bear_1: []}
        attacker = game.declare_blocker_step(attacker)

        assert bear_1 in attacker.keys()
        assert bear_2 in attacker[bear_1]
        assert len(attacker[bear_1]) == 1
        game.can_block.assert_called_once()
        game.can_be_blocked.assert_called_once()
        game.p2.binary_choice.assert_called_once()
        game.priority.assert_called_once_with(sorcery_speed=False)     

    def test_creature_can_only_block_first_attacker(self, game, mock_bear_factory):
        """First attacker is blocked and then cannot block the second attacker."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        bear_3 = mock_bear_factory()
        bear_1.tapped = True # attacker
        bear_2.tapped = True # attacker
        game.p1.creatures = [bear_1, bear_2]
        game.p2.creatures = [bear_3]
        game.p2.binary_choice = MagicMock(return_value=True)
        game.can_block = MagicMock(return_value=True)
        game.can_be_blocked = MagicMock(return_value=True)
        game.priority = MagicMock()

        attacker = {bear_1: [], bear_2: []}
        attacker = game.declare_blocker_step(attacker)

        assert bear_1 in attacker.keys()
        assert bear_2 in attacker.keys()
        assert bear_3 in attacker[bear_1]
        assert bear_3 not in attacker[bear_2]
        assert len(attacker[bear_1]) == 1
        assert len(attacker[bear_2]) == 0
        game.can_block.assert_called_once()
        game.can_be_blocked.assert_called_once()
        game.p2.binary_choice.assert_called_once()
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_creature_only_blocks_second_attacker(self, game, mock_bear_factory):
        """Creature does not block first attacker and then blocks the second attacker."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        bear_3 = mock_bear_factory()
        bear_1.tapped = True # attacker
        bear_2.tapped = True # attacker
        game.p1.creatures = [bear_1, bear_2]
        game.p2.creatures = [bear_3]
        game.p2.binary_choice = MagicMock(side_effect=[False, True])
        game.can_block = MagicMock(return_value=True)
        game.can_be_blocked = MagicMock(return_value=True)
        game.priority = MagicMock()

        attacker = {bear_1: [], bear_2: []}
        attacker = game.declare_blocker_step(attacker)

        assert bear_1 in attacker.keys()
        assert bear_2 in attacker.keys()
        assert bear_3 not in attacker[bear_1]
        assert bear_3 in attacker[bear_2]
        assert len(attacker[bear_1]) == 0
        assert len(attacker[bear_2]) == 1
        game.can_block.assert_called_once()
        assert game.can_be_blocked.call_count == 2
        assert game.p2.binary_choice.call_count == 2
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_creature_cannot_block(self, game, mock_bear_factory):
        """Creature cannot block so the player cannot declare it as blocker."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        bear_1.tapped = True # attacker
        game.p1.creatures = [bear_1]
        game.p2.creatures = [bear_2]
        game.p2.binary_choice = MagicMock()
        game.can_block = MagicMock(return_value=False)
        game.can_be_blocked = MagicMock()
        game.priority = MagicMock()

        attacker = {bear_1: [], bear_2: []}
        attacker = game.declare_blocker_step(attacker)

        assert bear_1 in attacker.keys()
        assert bear_2 not in attacker[bear_1]
        assert len(attacker[bear_1]) == 0
        game.p2.binary_choice.assert_not_called()
        game.can_block.assert_called_once()
        game.can_be_blocked.assert_not_called()
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_one_creature_cannot_block_but_second_can(self, game, mock_bear_factory):
        """Player can only declare one creature as blocker."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        bear_3 = mock_bear_factory()
        bear_1.tapped = True # attacker
        game.p1.creatures = [bear_1]
        game.p2.creatures = [bear_2, bear_3]
        game.p2.binary_choice = MagicMock(return_value=True)
        game.can_block = MagicMock(side_effect=[True, False])
        game.can_be_blocked = MagicMock(return_value=True)
        game.priority = MagicMock()

        attacker = {bear_1: []}
        attacker = game.declare_blocker_step(attacker)

        assert bear_1 in attacker.keys()
        assert bear_2 in attacker[bear_1]
        assert bear_3 not in attacker[bear_1]
        assert len(attacker[bear_1]) == 1
        game.p2.binary_choice.assert_called_once()
        assert game.can_block.call_count == 2
        game.can_be_blocked.assert_called_once()
        game.can_be_blocked.assert_called_once()
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_one_creature_cannot_block_attacker_but_second_can(self, game, mock_bear_factory):
        """Player can only declare one creature as blocker."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        bear_3 = mock_bear_factory()
        bear_1.tapped = True # attacker
        game.p1.creatures = [bear_1]
        game.p2.creatures = [bear_2, bear_3]
        game.p2.binary_choice = MagicMock(return_value=True)
        game.can_block = MagicMock(return_value=True)
        game.can_be_blocked = MagicMock(side_effect=[True, False])
        game.priority = MagicMock()

        attacker = {bear_1: []}
        attacker = game.declare_blocker_step(attacker)

        assert bear_1 in attacker.keys()
        assert bear_2 in attacker[bear_1]
        assert bear_3 not in attacker[bear_1]
        assert len(attacker[bear_1]) == 1
        game.p2.binary_choice.assert_called_once()
        assert game.can_block.call_count == 2
        assert game.can_be_blocked.call_count == 2
        game.p2.binary_choice.assert_called_once()
        game.priority.assert_called_once_with(sorcery_speed=False)

    # HELPER: DEAL DAMAGE TO CREATURE

    def test_creature_deals_damage_to_creature(self, game, mock_bear_factory):
        """One creature damages another. Happypath."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        dmg = bear_1.get_power()
        
        game.deal_combat_damage_to_creature(bear_1, bear_2, game.p1, game.p2)

        assert bear_2.damage_counter == dmg
        assert bear_1.damage_counter == 0

    def test_creature_deals_partial_damage_to_creature(self, game, mock_bear_factory):
        """One creature damages another by different amount than its power."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        DMG = 1
        
        game.deal_combat_damage_to_creature(bear_1, bear_2, game.p1, game.p2, DMG)

        assert bear_2.damage_counter == DMG
        assert bear_1.damage_counter == 0

    def test_trample_deals_excess_damage_to_player(self, game, mock_bear, mock_trample_dino):
        """Trampling dino deals excess damage to player blocking with a bear."""
        game.p1.creatures = [mock_trample_dino]
        game.p2.creatures = [mock_bear]
        game.deal_combat_damage_to_player = MagicMock()

        game.deal_combat_damage_to_creature(mock_trample_dino, mock_bear, game.p1, game.p2)

        assert mock_bear.damage_counter == mock_bear.get_toughness()
        excess_dmg = mock_trample_dino.get_power() - mock_bear.get_toughness()
        game.deal_combat_damage_to_player.assert_called_once_with(
            mock_trample_dino, game.p2, amount=excess_dmg,
        )

    def test_trample_does_not_trigger_for_bigger_blocker(self, game, mock_bear, mock_trample_dino):
        """Trampling dino deals excess damage to player when blocking a bear."""
        game.p1.creatures = [mock_bear]
        game.p2.creatures = [mock_trample_dino]
        game.deal_combat_damage_to_player = MagicMock()

        game.deal_combat_damage_to_creature(mock_bear, mock_trample_dino, game.p1, game.p2)

        game.deal_combat_damage_to_player.assert_not_called()

    def test_trample_does_not_trigger_for_smaller_attacker(self, game, mock_bear, mock_trample_dino):
        """Trampling Bear deals no damage to player when blocked by bigger dino."""
        game.p1.creatures = [mock_bear]
        game.p2.creatures = [mock_trample_dino]
        mock_bear.has_trample = MagicMock(return_value=True)
        game.deal_combat_damage_to_player = MagicMock()

        game.deal_combat_damage_to_creature(mock_bear, mock_trample_dino, game.p1, game.p2)

        game.deal_combat_damage_to_player.assert_not_called()

    def test_trample_does_not_trigger_against_same_size_creature(self, game, mock_bear, mock_trample_dino):
        """Trampling Bear deals no damage to player when blocked by bigger dino."""
        game.p1.creatures = [mock_trample_dino]
        game.p2.creatures = [mock_bear]
        mock_bear.base_power = 6
        mock_bear.base_toughness = 6
        game.deal_combat_damage_to_player = MagicMock()

        game.deal_combat_damage_to_creature(mock_trample_dino, mock_bear, game.p1, game.p2)

        game.deal_combat_damage_to_player.assert_not_called()

    # HELPER: DEAL DAMAGE TO PLAYER

    def test_creature_deals_damage_to_player(self, game, mock_bear):
        """One creature damages a player. Happypath."""
        dmg = mock_bear.get_power()
        hp = game.p2.life

        game.deal_combat_damage_to_player(mock_bear, game.p2)

        assert game.p2.life == hp - dmg

    def test_creature_deals_partial_damage_to_player(self, game, mock_bear):
        """One creature damages a player by different amount than its power."""
        hp = game.p2.life
        DMG = 1

        game.deal_combat_damage_to_player(mock_bear, game.p2, DMG)

        assert game.p2.life == hp - DMG

    # HELPER: ASSIGN COMBAT DAMAGE

    def test_single_assignment_hits_first_of_two_blocker(self, game, mock_bear_factory):
        """When double blocking, damage assignment should only go to first bear."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        bear_3 = mock_bear_factory()

        game.assign_combat_damage(bear_1, [bear_2, bear_3])



    # DAMAGE STEP

    def test_no_blocker_goes_to_player(self, game, mock_bear):
        """If no blocker is declared, the player takes combat damage."""
        attacker = {mock_bear: []}
        game.p1.creatures = [mock_bear]
        game.state_based_actions = MagicMock()
        game.priority = MagicMock()
        game.deal_combat_damage_to_player = MagicMock()

        game.damage_step(attacker)

        game.deal_combat_damage_to_player.assert_called_once()
        game.priority.assert_called_once_with(sorcery_speed=False)
        game.state_based_actions.assert_called_once()

    def test_one_blocker_damages_creature(self, game, mock_bear_factory):
        """If one blocker is declared, the blocker takes all the damage."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        game.p1.creatures = [bear_1]
        game.p2.creatures = [bear_2]
        attacker = {bear_1: [bear_2]}
        game.state_based_actions = MagicMock()
        game.priority = MagicMock()
        game.deal_combat_damage_to_creature = MagicMock()

        game.damage_step(attacker)

        assert game.deal_combat_damage_to_creature.call_count == 2
        game.priority.assert_called_once_with(sorcery_speed=False)
        game.state_based_actions.assert_called_once()

    def test_two_blocker_share_damage(self, game, mock_bear_factory):
        """If multiple blocker are declared, they share the damage."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        bear_3 = mock_bear_factory()
        game.p1.creatures = [bear_1]
        game.p2.creatures = [bear_2, bear_3]
        attacker = {bear_1: [bear_2, bear_3]}
        game.state_based_actions = MagicMock()
        game.priority = MagicMock()
        game.assign_combat_damage = MagicMock()

        game.damage_step(attacker)

        game.assign_combat_damage.assert_called_once()
        game.priority.assert_called_once_with(sorcery_speed=False)
        game.state_based_actions.assert_called_once()

    def test_removed_attacker_skips_damage_distribution(self, game, mock_bear_factory):
        """If an attacker is removed from play, it does not deal damage anymore."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        game.p2.creatures = [bear_2]
        attacker = {bear_1: [bear_2]}
        game.state_based_actions = MagicMock()
        game.priority = MagicMock()
        game.assign_combat_damage = MagicMock()

        game.damage_step(attacker)

        game.assign_combat_damage.assert_not_called()
        game.priority.assert_called_once_with(sorcery_speed=False)
        game.state_based_actions.assert_called_once()

    def test_removed_blocker_skips_damage_alltogether(self, game, mock_bear_factory):
        """If a blocker is removed from play, the attacker still does no damage at all."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        game.p1.creatures = [bear_1]
        attacker = {bear_1: [bear_2]}
        game.state_based_actions = MagicMock()
        game.priority = MagicMock()
        game.deal_combat_damage_to_creature = MagicMock()
        game.assign_combat_damage = MagicMock()
        game.deal_combat_damage_to_player = MagicMock()

        game.damage_step(attacker)

        game.deal_combat_damage_to_creature.assert_not_called()
        game.deal_combat_damage_to_player.assert_not_called()
        game.assign_combat_damage.assert_not_called()
        game.priority.assert_called_once_with(sorcery_speed=False)
        game.state_based_actions.assert_called_once()

    # END OF COMBAT

    def test_end_of_combat_has_priority(self, game):
        """End of combat has a single instant speed priority."""
        game.priority = MagicMock()

        game.end_of_combat_step()

        game.priority.assert_called_once_with(sorcery_speed=False)

    # PUTTING IT ALL TOGETHER

    def test_combat_phase_has_all_steps(self, game):
        """Combat phase has beginning of C., declare attackers, declare blocker, damage, end of C."""
        game.beginning_of_combat_step = MagicMock()
        game.declare_attacker_step = MagicMock()
        game.declare_blocker_step = MagicMock()
        game.damage_step = MagicMock()
        game.end_of_combat_step = MagicMock()

        game.combat_phase()

        game.beginning_of_combat_step.assert_called_once()
        game.declare_attacker_step.assert_called_once()
        game.declare_blocker_step.assert_called_once()
        game.damage_step.assert_called_once()
        game.end_of_combat_step.assert_called_once()


class TestEndPhase:
    """Test simulating end phase."""

    def test_beginning_of_end_phase_has_no_priority(self, game):
        """Beginning of end phase only triggers abilities."""
        game.priority = MagicMock()
        game.beginning_of_end_phase_step()
        game.priority.assert_not_called()

    def test_end_phase_has_instant_speed_priority(self, game):
        """End phase only has instant speed priority."""
        game.priority = MagicMock()
        game.end_step()
        game.priority.assert_called_once_with(sorcery_speed=False)

    def test_cleanup_removes_damage_counter(self, game, mock_bear_factory):
        """Damaged bears loose all damage counter on them."""
        bear_1 = mock_bear_factory()
        bear_2 = mock_bear_factory()
        bear_1.damage_counter = 2
        bear_2.damage_counter = 1
        game.p1.creatures = [bear_1]
        game.p2.creatures = [bear_2]

        game.cleanup_step()

        assert bear_1.damage_counter == 0
        assert bear_2.damage_counter == 0

    def test_cleanup_removes_eot_effects(self, game, mock_bear):
        """'Until end of turn' effect is removed."""
        x = Buff(target=mock_bear, power=3, toughness=3)
        mock_bear.modifiers = [x]
        game.p1.eot_effects = [x]

        assert mock_bear.get_power() == 5
        assert mock_bear.get_toughness() == 5

        game.cleanup_step()

        assert x not in mock_bear.modifiers
        assert len(mock_bear.modifiers) == 0
        assert x not in game.p1.eot_effects
        assert len(game.p1.eot_effects) == 0

    def test_cleanup_does_not_discard_at_seven_handcards(self, game, mock_bear_factory):
        """Discard until 7 or less cards are in hand."""
        game.p1.hand = [mock_bear_factory() for _ in range(7)]
        game.cleanup_step()
        assert len(game.p1.hand) == 7

    def test_cleanup_does_not_discard_at_seven_handcards(self, game, mock_bear_factory):
        """Discard until 7 or less cards are in hand."""
        game.p1.target = MagicMock(return_value=0)
        game.p1.hand = [mock_bear_factory() for _ in range(10)]
        game.cleanup_step()
        assert len(game.p1.hand) == 7


class TestHelperMethods:
    """Test misc helper methods that are part of the game."""

    # PLAYING LANDS
    
    def test_play_land_happypath(self, game, mock_land):   
        """Playing a land makes the landdrop correctly."""
        data = build_priority_data(game)
        game.p1.hand = [mock_land]
        game.put_action_on_stack = MagicMock()

        game.play_land(data, mock_land)

        assert game.hit_landdrop == True
        assert mock_land not in game.p1.hand, "Land Should have been removed from Hand."
        assert mock_land in game.p1.lands, "Land should have appeard on the Field."
        assert game.hit_landdrop, "Landdrop has been made."
        game.put_action_on_stack.assert_not_called()

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
        # ToDo: mana cost for abilities
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
        # ToDo: mana cost for abilities
        data.priority_player.pay_for_manacost.assert_not_called()
        mock_bear.activated_ability.pay_cost.assert_not_called()
        mock_bear.activated_ability.activity.assert_not_called()
        game.put_action_on_stack.assert_not_called()

    def test_activate_mana_ability_can_activate(self, game, mock_land):
        """Activating a mana ability instantly resolves."""
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=True)

        game.activate_ability(data, mock_land)

        mock_land.activated_ability.can_activate.assert_called_once_with(
            mock_land, data.priority_player, data.non_priority_player,
        )
        mock_land.activated_ability.choose_targets.assert_called_once_with(
            mock_land, data.priority_player, data.non_priority_player,
        )
        # ToDo: mana cost for abilities
        data.priority_player.pay_for_manacost.assert_not_called()
        mock_land.activated_ability.pay_cost.assert_called_once_with(
            mock_land, data.priority_player, data.non_priority_player,
        )
        mock_land.activated_ability.activity.assert_called_with(
            mock_land, data.priority_player, data.non_priority_player,
        )
        game.put_action_on_stack.assert_not_called()

    def test_activate_mana_ability_can_not_activate(self, game, mock_land):
        """Mana ability cant activate and does not resolve."""
        data = build_priority_data(game)
        game.put_action_on_stack = MagicMock()
        game.p1.pay_for_manacost = MagicMock(return_value=True)
        mock_land.activated_ability.can_activate = MagicMock(return_value=False)

        game.activate_ability(data, mock_land)

        mock_land.activated_ability.can_activate.assert_called_once_with(
            mock_land, data.priority_player, data.non_priority_player,
        )
        mock_land.activated_ability.choose_targets.assert_not_called()
        # ToDo: mana cost for abilities
        data.priority_player.pay_for_manacost.assert_not_called()
        mock_land.activated_ability.pay_cost.assert_not_called()
        mock_land.activated_ability.activity.assert_not_called()
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
