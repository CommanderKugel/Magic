from Player.Player import Player
from Magic.Card import Card, Creature, Land, Sorcery, Instant
from Magic.Stack import StackObject
from Magic.Library import shuffle_library


class Game:
    """Game sim of Magic: the gathering, only supporting 2 players for now."""
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
            f"\n"
            f"[STACK] {[s.name for s in self.stack]}\n"
            f"[OWN MANA] {self.active_player.floating_mana}\n"
        )

    def prepare_game(self) -> None:
        """Shuffle the library, then draw 7 cards."""
        for player in [self.p1, self.p2]:
            shuffle_library(player.library)
            player.draw(7)

    def prepare_turn(self) -> None:
        """Reset some values in preparation of the game."""
        # for active player: assume there are only 2 players for now.
        self.turn += 1
        self.active_player = self.p1 if self.turn % 2 else self.p2
        self.reactive_player = self.p2 if self.turn % 2 else self.p1
        self.hit_landdrop = False

    def play_turn(self) -> None:
        """Play a whole turn of the game."""
        
        self.prepare_turn()
        print("[PLAY TURN] active player:", self.active_player.name)

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
            attacker = {}
            for creature in self.active_player.creatures:
                if self.active_player.binary_choice(
                    f"Do you want to attack with {creature.name}?"
                ):
                    attacker[creature] = []
                    print(f"[ATTACKER] attacking with {creature.name}")
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
                        print(f"[BLOCKER] blocking {att.name} with {blocker.name}")
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
                    print(f"[DAMAGE] {self.reactive_player.name} receivec {attacker.power} dmg.")
                # only one blocker
                # equal trade of damage.
                elif len(blocker) == 1:
                    block = blocker[0]
                    block.damage_counter += attacker.power
                    attacker.damage_counter += block.power
                    print(f"[DAMAGE] {block.name} received {attacker.power} dmg and {attacker.name} received {block.power} dmg.")
                elif len(blocker) > 1:
                    damage_dist = self.active_player.distribute_damage_to_blocker(attacker, blocker)
                    assert sum(damage_dist.values()) <= attacker.power
                    for block in blocker:
                        block.damage_counter += damage_dist.get(block, 0)

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
        loosers = []
        for player in [self.p1, self.p2]:
            if player.life <= 0:
                loosers.append(player)
            for creature in player.creatures:
                if creature.damage_counter >= creature.toughness:
                    print(f"[STATE BASED ACTIONS] {creature.name} dies due to damage.")
                    player.graveyard.append(creature)
                    player.creatures.remove(creature)
        if len(loosers) == 1:
            winner = self.p1 if self.p1 not in loosers else self.p2
            raise Exception(winner.name)
        if len(loosers) == 2:
            raise Exception("Draw")

    def priority(self, sorcery_speed: bool = False) -> None:
        """Handle passing of the priority between players using a state-machine."""
        self.stack: list[StackObject] = []

        STATE_5 = "Action"
        STATE_6 = "Passing"
        STATE_7 = "RESOLVE"

        # 1. Beginning of Step/Phase
        # 2. State based actions
        # 3. Triggered Abilities
        # 4. Active Player receives priority
        priority_player = self.active_player
        non_priority_player = self.reactive_player

        # look at concepts/Stack.md for more details
        state = STATE_5
        pass_counter = 0
        while True:
            # 5. Player with Priority may choose an action
            if state == STATE_5:
                (action, card) = priority_player.choose_action(
                    sorcery_speed=(
                        sorcery_speed 
                        and (len(self.stack) == 0) 
                        and (priority_player is self.active_player)
                    ),
                    hit_landdrop=self.hit_landdrop and sorcery_speed,
                    opponent=non_priority_player,
                )

                # Playing lands
                if action == "Play" and isinstance(card, Land):
                    assert priority_player is self.active_player
                    assert len(self.stack) == 0
                    assert card in priority_player.hand
                    print("Playing a Land:", card.name)
                    priority_player.lands.append(card)
                    priority_player.hand.remove(card)
                    self.hit_landdrop = True
                    # goto 5., no reaction to land drops
                    print(f"[PLAY] {priority_player.name} played {card.name}")
                    continue

                # Mana Abilities
                if action == "Ability" and card.activated_ability.is_mana_ability:
                    print("Activating an Ability:", card.name)
                    ability = card.activated_ability
                    if not ability.can_activate(card, priority_player, non_priority_player):
                        print(f"[OOPS] {priority_player.name} messed up Ablity of {card.name}")
                        continue
                    # instantly resolve mana abilities - they dont use the stack
                    ability.pay_cost(card, priority_player, non_priority_player)
                    ability.activity(card, priority_player, non_priority_player)
                    # goto 5.
                    print(f"[ABILITY] {priority_player.name} activated Ability of {card.name}")
                    continue

                # Put all other actions on the stack
                if action != "Pass":
                    assert not (action == "Ability" and card.activated_ability.is_mana_ability)
                    assert not (action == "Play" and isinstance(card, Land))

                    # Pay cost for Activated Abilities
                    if action == "Ability":
                        if not card.activated_ability.can_activate(card, priority_player, non_priority_player):
                            print(f"[OOPS] {priority_player.name} messed up activation cost of {card.name}")
                            continue
                        card.activated_ability.pay_cost(card, priority_player, non_priority_player)

                    # Pay cost for casting spells
                    if action == "Cast":

                        # Pay Manacost
                        if not priority_player.pay_for_manacost(card, non_priority_player):
                            print(f"[OOPS] {priority_player.name} messed up Mana cost of {card.name}")
                            continue

                        # Pay extra cost for instants and sorceries, e.g. choose targets
                        if isinstance(card, (Instant, Sorcery)):
                            if not card.ability.can_activate(
                                card, priority_player, non_priority_player
                            ):
                                print(f"[OOPS] {priority_player.name} messed up activation cost of {card.name}")
                                continue
                            card.ability.pay_cost(card, priority_player, non_priority_player)
                            
                        priority_player.hand.remove(card)

                    x = "ABILITY" if action == "Ability" else "CASE"
                    print(f"[{x}] {priority_player.name} plays {card.name}")
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
                    pass_counter += 1
                    state = STATE_6
                    print(f"[PASSING] {priority_player.name} passes")
                    continue
            
            # 6. Priority was passed
            if state == STATE_6:
                self.state_based_actions()

                # give priority to opponent
                if pass_counter < 2:
                    if priority_player == self.active_player:
                        priority_player = self.reactive_player
                        non_priority_player = self.active_player
                    else:
                        priority_player = self.active_player
                        non_priority_player = self.reactive_player

                    # goto 5.
                    state = STATE_5
                    continue

                # all players passed
                state = STATE_7
            
            # 7. Resolve stack
            if state == STATE_7:

                # End prioroty juggling if stack is empty.
                if len(self.stack) == 0:
                    return
                
                # remove Card from stack
                stack_object = self.stack.pop(-1)
                action = stack_object.action
                card = stack_object.source
                owner = stack_object.owner
                opponent = self.p2 if owner is self.p1 else self.p1

                x = "Ability" if action == "Ability" else "Cast"
                print(f"[RESOLVE] resolving {x} of {card.name}")

                # resolve Casting Spells
                if stack_object.action == "Cast":

                    # Creature -> put it on the field
                    if isinstance(card, Creature):
                        owner.creatures.append(card)
                        # ToDo: ETB

                    # Sorceries or Instants -> resolve abilities
                    if isinstance(card, (Instant, Sorcery)):
                        card.ability.activity(card, owner, opponent)
                
                # resolve Activated or Triggered Abilities
                # ToDo: collect targets on stack object (maybe dict?)
                if stack_object.action == "Ability":
                    card.activated_ability.activity(card, owner, opponent)

                self.state_based_actions()

                # goto 3.
                priority_player = self.active_player
                non_priority_player = self.reactive_player
                state = STATE_5
                pass_counter = 0
