from typing import Literal

from Player.Player import Player
from Magic.Card import Card, Creature, Land
from Magic.Library import shuffle_library
from Magic.Stack import StackObject

# for now only 2 players

class Game:
    def __init__(self, p1: Player, p2: Player):
        self.p1 = p1
        self.p2 = p2
        
        self.turn = 0
        self.active_player = None
        self.reactive_player = None

        self.step = None
        self.hit_landdrop = False

        self.stack: list[StackObject] = []

    def __repr__(self):
        return (
            f"[OPP LAND]      {[c.name for c in self.reactive_player.lands]}\n"
            f"[OPP CREATURES] {[c.name for c in self.reactive_player.creatures]}\n"
            f"[OWN CREATURES] {[c.name for c in self.active_player.creatures]}\n"
            f"[OWN LAND]      {[c.name for c in self.active_player.lands]}\n"
            f"[OWN HAND]      {[c.name for c in self.active_player.hand]}\n"
            f"[OWN MANA] {self.active_player.floating_mana}\n"
        )

    def prepare(self) -> None:
        def prep(p: Player):
            shuffle_library(p.library)
            p.draw(7)
        prep(self.p1)
        prep(self.p2)

    def play_turn(self) -> None:
        """Play a whole turn of the game."""
        # for active player: assume there are only 2 players for now.
        self.turn += 1
        self.active_player = self.p1 if self.turn % 2 else self.p2
        self.reactive_player = self.p2 if self.turn % 2 else self.p1
        self.hit_landdrop = False

        self.beginning_phase()
        self.main_phase()
        self.combat_phase()
        self.main_phase()
        self.end_phase()

    def clear_player_mana(self) -> None:
        """Clear all players floating mana. Helper method."""
        self.p1.clear_floating_mana()
        self.p2.clear_floating_mana()
    
    def beginning_phase(self) -> None:
        """Play the whole beginning phase of this turn."""

        def untap_step():
            """Play the untap step."""
            print("[UNTAP]")
            self.step = "Untap"
            # ToDo: Triggered Abilities
            self.priority(sorcery_speed=False)

            for creature in self.active_player.creatures:
                creature.tapped = False
            for land in self.active_player.lands:
                land.tapped = False

        def upkeep_step():
            """Play the Upkeep step."""
            print("[UPKEEP]")
            self.step = "Upkeep"
            self.priority(sorcery_speed=False)

        def draw_step():
            """Play the Draw step."""
            print("[DRAW]")
            self.step = "Draw"
            # ToDo: priority
            self.active_player.draw(1)
        
        untap_step()
        upkeep_step()
        draw_step()
        self.clear_player_mana()
    
    def main_phase(self) -> None:
        """Play a whole main phase. There are two per turn, most of the time."""
        # ToDo: Beginning of main phase triggers
        print("[MAIN PHASE]")
        self.step = "Main"
        self.priority(sorcery_speed=True)
        self.clear_player_mana()

    def combat_phase(self) -> None:
        """Play a whole combat phase."""

        def beginning_of_combat() -> None:
            """Play beginning of combat step."""
            print("[BEGINNING OF COMBAT]")
            self.step = "BeginningOfCombat"
            # ToDo: triggered abilities
            self.priority(sorcery_speed=False)

        def declare_attackers() -> dict[Creature, list[Creature]]:
            """Declare this turns attacker."""
            print("[DECLARE ATTACKERS STEP]")
            self.step = "DeclareAttacker"
            attacker = {
                creature: []
                for creature in self.active_player.creatures
                if self.active_player.binary_choice(
                    f"Do you want to attack with {creature.name}?"
                )
            }
            self.priority(sorcery_speed=False)
            return attacker

        def declare_blockers(attacker: dict[Creature, list[Creature]]) -> dict[Creature, list[Creature]]:
            """Declare blocker to this turns attackers."""
            print("[DECLARE BLOCKERS STEP]")
            self.step = "DeclareBlocker"
            available_blocker = [c for c in self.reactive_player.creatures]
            for att in attacker.keys():
                for blocker in available_blocker:
                    if self.reactive_player.binary_choice(
                        f"Do you want to block {att.name} with {blocker.name}?"
                    ):
                        attacker[att].append(blocker)
                        available_blocker.remove(blocker)
            self.priority(sorcery_speed=False)
            return attacker

        def damage_step(attacker_: dict[Creature, list[Creature]]) -> None:
            """Deal combat damage to creatures and players."""
            print("[DAMAGE STEP]")
            self.step = "Damage"

            for attacker, blocker in attacker_.items():
                # no blocker: deal damage to opponent
                if len(blocker) == 0:
                    self.reactive_player.life -= attacker.power
                # only one blocker
                # equal trade of damage.
                elif len(blocker) == 1:
                    block = blocker[0]
                    block.damage_counter += attacker.power
                    attacker.damage_counter += block.power
                elif len(blocker) > 1:
                    raise NotImplementedError()

            # actually kill creatures and players
            self.state_based_actions()

        def end_of_combat() -> None:
            """Play end of combat step."""
            print("[END OF COMBAT STEP]")
            self.step = "EndOfCombat"
            self.priority(sorcery_speed=False)

        beginning_of_combat()
        attacker = declare_attackers()
        attacker = declare_blockers(attacker)
        damage_step(attacker)
        end_of_combat()
        self.clear_player_mana()

    def end_phase(self) -> None:
        """Play a whole end phase."""

        def beginning_of_end_phase() -> None:
            """Play the beggning of the end phase."""
            print("[BEGINNING OF END PHASE]")
            self.step = "BeginnningOfEndPhase"
            # ToDo: triggered abilities
            pass

        def end_phase() -> None:
            """Play the end phase of this turn."""
            print("[END STEP]")
            self.step = "EndStep"
            self.priority(sorcery_speed=False)
            pass

        def cleanup_step() -> None:
            """Play the cleanup step of this turn.
            - remove damage counter from creatures.
            """
            print("[CLEANUP STEP]")
            self.step = "CleanupStep"
            # remove damage countes from creatures
            for p in [self.p1, self.p2]:
                for creature in p.creatures:
                    creature.damage_counter = 0
                # remove floating mana
                p.clear_floating_mana()
            # discard due to handsize
            while len(self.active_player.hand) > 7:
                print("Discard due to handsize.")
                card = self.active_player.target(own_hand=True)
                self.active_player.discard(card)

        beginning_of_end_phase()
        end_phase()
        cleanup_step()
        self.clear_player_mana()

    def state_based_actions(self) -> None:
        """Perform state based actions on this game. Only player life and creature dmg for now."""
        for player in [self.p1, self.p2]:
            if player.life <= 0:
                print(f"Player {player} lost the game!")
                raise
            for creature in player.creatures:
                if creature.damage_counter >= creature.toughness:
                    print(f"[STATE BASED ACTIONS] {creature.name} dies due to damage.")
                    player.graveyard.append(creature)
                    player.creatures.remove(creature)

    def priority(self, sorcery_speed: bool = False) -> None:
        """Handle passing of the priority between players using a state-machine."""
        print(self)
        self.stack: list[StackObject] = []

        STATE_5 = "Action"
        STATE_6 = "Passing"
        STATE_7 = "RESOLVE"

        # 1. Beginning of Step/Phase
        # 2. State based actions
        # 3. Triggered Abilities
        # 4. Active Player receives priority
        priority_player = self.active_player

        # look at concepts/Stack.md for more details
        state = STATE_5
        pass_counter = 0
        while True:
            print("[STATE]", state)
            print("Priority Player:", priority_player.name, "\n")

            # 5. Player with Priority may choose an action
            if state == STATE_5:
                (action, card) = priority_player.choose_action_dummy(
                    sorcery_speed=sorcery_speed and (len(self.stack) == 0) and (priority_player is self.active_player),
                    hit_landdrop=self.hit_landdrop and sorcery_speed,
                )

                # Playing lands
                if action == "Play" and isinstance(card, Land):
                    assert priority_player is self.active_player
                    assert len(self.stack) == 0
                    assert card in priority_player.hand
                    print("Playing a Land:", card.name)
                    priority_player.play_land_from_hand(card)
                    self.hit_landdrop = True
                    # goto 5., no reaction to land drops
                    continue

                # Mana Abilities
                if action == "Ability" and card.activated_ability.is_mana_ability:
                    print("Activating an Ability:", card.name)
                    ability = card.activated_ability
                    if not ability.can_activate(card, priority_player):
                        continue
                    ability.pay_cost(card, priority_player)
                    ability.activity(card, priority_player)
                    # goto 5., no reaction to mana abilities
                    continue

                # Put all other actions on the stack
                if action != "Pass":
                    assert not (action == "Ability" and card.activated_ability.is_mana_ability)
                    assert not (action == "Play" and isinstance(card, Land))

                    if action == "Ability":
                        print("Checking Ability requirements:", card.name)
                        if not card.activated_ability.can_activate(card, priority_player):
                            print(f"Activation requirements for activated_ability of {card.name} are not met.")
                            continue
                        card.activated_ability.pay_cost(card, priority_player)

                    if action == "Cast" and not priority_player.pay_for_manacost(card):
                        print("Paying Mana to cast Creature:", card.name)
                        print(f"Could not pay for manacost of {card.name}.")
                        continue

                    print("Putting Action on the stack:", action, card.name)
                    stack_object = StackObject(
                        action=action,
                        source=card,
                        owner=priority_player,
                    )
                    self.stack.append(stack_object)
                    pass_counter = 0

                    # goto 5., keep priority
                    continue
                
                # Passing
                else:
                    print("Passing.")
                    pass_counter += 1
                    state = STATE_6
            
            # 6. Priority was passed
            if state == STATE_6:

                self.state_based_actions()

                # give priority to opponent
                if pass_counter < 2:
                    print("Giving Priority to opponent.")
                    priority_player = (
                        self.reactive_player
                        if priority_player is self.active_player
                        else self.active_player
                    )
                    # goto 5.
                    state = STATE_5
                    continue

                # all players passed
                print("All Players have Passed.")
                state = STATE_7
            
            # 7. Resolve stack
            if state == STATE_7:
                print("Resolving the Stack.")

                # End prioroty juggling if stack is empty.
                if len(self.stack) == 0:
                    print("Nothing left on the stack to resolve. Returning now.")
                    return
                
                stack_object = self.stack.pop(-1)
                action = stack_object.action
                card = stack_object.source
                owner = stack_object.owner

                # resolve Casting Creatures
                if stack_object.action == "Cast" and isinstance(card, Creature):
                    print("Resolving casting a Creature:", card.name)
                    stack_object.owner.play_creature_from_hand(card)
                    # ToDo: ETB
                
                # resolve Activated or Triggered Abilities
                # ToDo: collect targets on stack object (maybe dict?)
                if stack_object.action == "Ability":
                    print("Resolving an Ability:", card.name)
                    card.activated_ability.activity(card, owner)

                # goto 3.
                priority_player = self.active_player
                state = STATE_5
                pass_counter = 0
