from src.Player.Player import Player
from src.Magic.Card import Card, Creature, Land, Sorcery, Instant
from src.Magic.Stack import StackObject, PriorityData
from src.Magic.Library import shuffle_library
from src.Magic.Buff import Buff
from src.Magic.Literals import PriorityState, Action

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
                    self.reactive_player.life -= attacker.get_power()
                    print(f"[DAMAGE] {self.reactive_player.name} receivec {attacker.get_power()} dmg.")
                # only one blocker
                # equal trade of damage.
                elif len(blocker) == 1:
                    block = blocker[0]
                    block.damage_counter += attacker.get_power()
                    attacker.damage_counter += block.get_power()
                    print(f"[DAMAGE] {block.name} received {attacker.get_power()} dmg and {attacker.name} received {block.power} dmg.")
                elif len(blocker) > 1:
                    damage_dist = self.active_player.distribute_damage_to_blocker(attacker, blocker)
                    assert sum(damage_dist.values()) <= attacker.get_power()
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
                for eot in p.eot_effects:
                    if isinstance(eot, Buff):
                        eot.target.buffs.remove(eot)
                        p.eot_effects.remove(eot)
                        del eot
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
                if creature.damage_counter >= creature.get_toughness():
                    print(f"[STATE BASED ACTIONS] {creature.name} dies due to damage.")
                    player.graveyard.append(creature)
                    player.creatures.remove(creature)
        if len(loosers) == 1:
            winner = self.p1 if self.p1 not in loosers else self.p2
            raise Exception(winner.name)
        if len(loosers) == 2:
            raise Exception("Draw")


    def play_land(self, data: PriorityData, card: Land) -> None:
        """Play a land for priority player."""
        assert data.priority_player is self.active_player
        assert len(self.stack) == 0
        assert card in data.priority_player.hand
        assert card not in data.priority_player.lands
        print("Playing a Land:", card.name)
        data.priority_player.lands.append(card)
        data.priority_player.hand.remove(card)
        self.hit_landdrop = True
        # goto 5., no reaction to land drops
        print(f"[PLAY] {data.priority_player.name} played {card.name}")

    def activate_mana_ability(self, data: PriorityData, card: Card) -> None:
        """Try activating an ability. Return True if can activate, False if not."""
        print("Activating an Ability:", card.name)
        ability = card.activated_ability
        if not ability.can_activate(card, data.priority_player, data.non_priority_player):
            print(f"[OOPS] {data.priority_player.name} messed up Ablity of {card.name}")
            return
        # instantly resolve mana abilities - they dont use the stack
        ability.pay_cost(card, data.priority_player, data.non_priority_player)
        ability.activity(card, data.priority_player, data.non_priority_player)
        # goto 5.
        print(f"[ABILITY] {data.priority_player.name} activated Ability of {card.name}")

    def priority_pass(self, data: PriorityData) -> None:
        """Priority_player passes. Update state and increase pass counter."""
        data.pass_counter += 1
        data.state = "Passing"
        print(f"[PASSING] {data.priority_player.name} passes")

    def put_action_on_stack(self, data: PriorityData, action: Action, card: Card) -> None:
        """Put an Ability or Cast of a spell on the stack. Reset the pass counter. State is 'Action'."""
        print(f"[{"ABILITY" if action == "Ability" else "CAST"}] {data.priority_player.name} plays {card.name}")
        stack_object = StackObject(
            action=action,
            source=card,
            owner=data.priority_player,
        )
        self.stack.append(stack_object)
        data.pass_counter = 0
        data.state = "Action"

    def activate_ability(self, data: PriorityData, card: Card) -> None:
        """Activate an ability. Pay its cost and put it on the stack. Keep priority."""
        if not card.activated_ability.can_activate(card, data.priority_player, data.non_priority_player):
            print(f"[OOPS] {data.priority_player.name} messed up activation cost of {card.name}")
            return
        card.activated_ability.pay_cost(card, data.priority_player, data.non_priority_player)
        self.put_action_on_stack(data, "Ability", card)

    def cast_spell(self, data: PriorityData, card: Card) -> None:
        """Cast a spell. Pay its cost, remove it from hand and put it on the stack. Keep priority."""
        # Pay Manacost
        if not data.priority_player.pay_for_manacost(card, data.non_priority_player):
            print(f"[OOPS] {data.priority_player.name} messed up Mana cost of {card.name}")
            return
        # Pay extra cost for instants and sorceries, e.g. choose targets
        if isinstance(card, (Instant, Sorcery)):
            if not card.ability.can_activate(card, data.priority_player, data.non_priority_player):
                print(f"[OOPS] {data.priority_player.name} messed up activation cost of {card.name}")
                return
            card.ability.pay_cost(card, data.priority_player, data.non_priority_player)
        # remove card from hand
        data.priority_player.hand.remove(card)
        self.put_action_on_stack(data, "Cast", card)

    def swap_priority(self, data: PriorityData) -> None:
        """On 2 or less passes, non_active_player receives priority. Otherwise, resolve the next item on the stack."""
        self.state_based_actions()
        # single pass: give priority to opponent
        if data.pass_counter < 2:
            data.swap_priority()
            # goto 5.
            data.state = "Action"
        # all players passed: resolve top item from the stack
        data.state = "Resolve"
    
    def resolve_top_object_from_stack(self, data: PriorityData) -> None:
        """Pop and resolve the top item from the stack. Perform statebased actions. active player receives priority."""
        assert len(self.stack) > 0
        # remove Card from stack
        stack_object = self.stack.pop(-1)
        action = stack_object.action
        card = stack_object.source
        owner = stack_object.owner
        opponent = self.p2 if owner is self.p1 else self.p1
        print(f"[RESOLVE] resolving {"Ability" if action == "Ability" else "Cast"} of {card.name}")

        # resolve Casting Spells
        if stack_object.action == "Cast":
            # Creature -> put it on the field
            if isinstance(card, Creature):
                owner.creatures.append(card)
                # ToDo: 
                
            # Sorceries or Instants -> resolve abilities
            if isinstance(card, (Instant, Sorcery)):
                card.ability.activity(card, owner, opponent)
        
        # resolve Activated or Triggered Abilities
        if stack_object.action == "Ability":
            card.activated_ability.activity(card, owner, opponent)

        self.state_based_actions()

        # goto 3.
        data.priority_player = self.active_player
        data.non_priority_player = self.reactive_player
        data.state = "Action"
        data.pass_counter = 0

    def priority(self, sorcery_speed: bool = False) -> None:
        """Handle passing of the priority between players using a state-machine."""
        assert len(self.stack) == 0
        # 1. Beginning of Step/Phase
        # 2. State based actions
        # 3. Triggered Abilities
        # 4. Active Player receives priority
        # look at concepts/Stack.md for more details
        data = PriorityData(
            state="Action",
            priority_player=self.active_player,
            non_priority_player=self.reactive_player,
            pass_counter=0,
        )

        while True:
            # 5. Player with Priority may choose an action
            if data.state == "Action":
                so_sp = (
                    sorcery_speed 
                    and (len(self.stack) == 0) 
                    and (data.priority_player is self.active_player)
                )
                (action, card) = data.priority_player.choose_action(
                    sorcery_speed=so_sp,
                    hit_landdrop=self.hit_landdrop and sorcery_speed,
                    opponent=data.non_priority_player,
                )

                # Playing Lands
                if action == "Play" and isinstance(card, Land):
                    self.play_land(data, card)

                # Mana Abilities
                if action == "Ability" and card.activated_ability.is_mana_ability:
                    self.activate_mana_ability(data, card)

                # Passing
                if action == "Pass":
                    self.priority_pass(data)

                # Activate Abilities
                if action == "Ability" and not card.activated_ability.is_mana_ability:
                    self.activate_ability(data, card)

                # Cast Spells
                if action == "Cast":
                    self.cast_spell(data, card)

                # goto 5. if not passed, else go to 6.
                continue
            
            # 6. Priority was passed
            if data.state == "Passing":
                self.swap_priority(data)
                # goto 5. if one pass in a row, else goto 7.
            
            # 7. Resolve stack
            if data.state == "Resolve":
                if len(self.stack) == 0:
                    return
                self.resolve_top_object_from_stack(data)
                # goto 5. if stack resolved, else return
