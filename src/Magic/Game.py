from src.Player.Player import Player
from src.Magic.Card import Card, Creature, Land, Sorcery, Instant
from src.Magic.Stack import StackObject, PriorityData, PriorityState
from src.Magic.Library import shuffle_library
from src.Magic.Modifier import Modifier
from src.Magic.Literals import PriorityState, Action

class Game:
    """Game sim of Magic: the gathering, only supporting 2 players for now."""
    def __init__(self, p1: Player, p2: Player):
        self.p1 = p1
        self.p2 = p2
        
        self.turn = 0
        self.active_player: Player
        self.reactive_player: Player

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


    # BEGINNING PHASE


    def untap_step(self) -> None:
        """Play the untap step. See concepts/Turn.md for more info."""
        print("[UNTAP]")

        # ToDo: Triggered abilities
        # ToDo: Phasing
        # ToDo: day/night

        # untap all permanents active player controls
        # no priority in this step

        for creature in self.active_player.creatures:
            creature.tapped = False
            creature.summoning_sick = False

        for land in self.active_player.lands:
            land.tapped = False

    def upkeep_step(self) -> None:
        """Play the Upkeep step. See concepts/Turn.md for more info."""
        print("[UPKEEP]")

        # ToDo: Triggered abilities

        self.priority(sorcery_speed=False)

    def draw_step(self) -> None:
        """Play the Draw step. See concepts/Turn.md for more info."""
        print("[DRAW]")
        self.active_player.draw(1)
        self.priority(sorcery_speed=False)
    
    def beginning_phase(self) -> None:
        """Play the whole beginning phase of this turn. See concepts/Turn.md for more info."""        
        self.untap_step()
        self.upkeep_step()
        self.draw_step()
        self.clear_player_mana()


    # MAIN PHASE


    def main_phase(self) -> None:
        """
        Play a whole main phase. There are two per turn, most of the time.
        See concepts/Turn.md for more info.
        """
        # ToDo: Beginning of main phase triggers
        # ToDo: Sagas

        print("[MAIN PHASE]")

        self.priority(sorcery_speed=True)
        self.clear_player_mana()


    # COMBAT PHASE


    def beginning_of_combat_step(self) -> None:
        """Play beginning of combat step. See concepts/Turn.md for more info."""

        # ToDo: triggered abilities

        self.priority(sorcery_speed=False)

    def can_attack(self, creature: Creature, owner: Player) -> bool:
        """Returns True if the creature can attack, False if not."""

        # ToDo: summoning sickness
        # ToDo: haste
        # ToDo: defender
        # ToDo: cant attack

        return not creature.tapped and not creature.summoning_sick

    def wants_to_attack(self, creature: Creature, owner: Player) -> bool:
        """Binary choice if the creature should attack."""

        # ToDo: goad
        # ToDo: attacks each turn if able

        return owner.binary_choice(f"Do you wnat to attack with {creature.name}?")

    def declare_attacker_step(self) -> dict[Creature, list[Creature]]:
        """Declare this turns attacker. See concepts/Turn.md for more info."""

        # ToDo: Planeswalker

        attacker = {
            creature: []
            for creature in self.active_player.creatures

            if self.can_attack(creature, self.active_player)

            # ToDo: requirements (e.g. attacks if able)
            and self.wants_to_attack(creature, self.active_player)
        }
        
        # ToDo: attacker restrictions (e.g. cannot attack alone) -> remove from list
        # ToDo: determine extra cost -> activate mana abilities -> pay cost

        for att, _ in attacker.items():
            att.tapped = True
            print(f"[ATTACKER] {att.name}")

        # ToDo: Triggered abilities
        
        self.priority(sorcery_speed=False)
        return attacker

    def can_block(self, blocker: Creature, owner: Player) -> bool:
        """Returns True if the creature can block. Does not mean specific attacker can be blocked though."""

        # ToDo: cant block

        return not blocker.tapped

    def can_be_blocked(self, attacker: Creature, defender: Creature) -> bool:
        """Returns Ture if attacking creature can be blocked by blocker, False if not."""

        # Flying & Reach
        if attacker.is_flying() and not (defender.is_flying() or defender.has_reach()):
            return False

        # ToDo: protection
        # ToDo: cant be blocked

        return True

    def declare_blocker_step(self, all_attacker: dict[Creature, list[Creature]]) -> dict[Creature, list[Creature]]:
        """Declare blocker to this turns attackers. See concepts/Turn.md for more info."""

        # ToDo: pre-filter blocker for perfomance
        # -> is untapped, not summoningsick or has haste

        available_blocker = [
            creature 
            for creature in self.reactive_player.creatures
            if self.can_block(creature, self.reactive_player)
        ]

        unavailable_blocker = []

        for attacker in all_attacker.keys():
            for blocker in available_blocker:
                if blocker in unavailable_blocker:
                    continue

                if (
                    self.can_be_blocked(attacker, blocker)
                    and self.reactive_player.binary_choice(
                        f"Do you want to block {attacker.name} with {blocker.name}?"
                    )
                ):
                    # ToDo: determine extra costs -> activate mana abilities -> pay extra costs

                    # creature blocks attacker
                    all_attacker[attacker].append(blocker)

                    # creatures can only block one attacker at a time
                    unavailable_blocker.append(blocker)

        for attacker, b in all_attacker.items():
            for blocker in b:
                print(f"[BLOCK] {blocker.name} blocks {attacker.name}")
            if len(b) == 0:
                print(f"[BLOCK] unblocked - {attacker.name}")

        # ToDo: triggered abilities
                    
        self.priority(sorcery_speed=False)

        return all_attacker

    def deal_combat_damage_to_creature(
        self, 
        attacker: Creature, 
        victim: Creature,
        attacking_player: Player,
        defending_player: Player,
        amount: int | None = None
    ) -> None:
        """Attacker deals damage to the victim."""

        # ToDo: wither
        
        dmg = amount if amount is not None else attacker.get_power()
        toughness = victim.get_toughness()

        # Trample
        if (
            attacker.has_trample() 
            and dmg > toughness
            and attacking_player == self.active_player
        ):
            trample_dmg = dmg - toughness
            dmg = toughness
            self.deal_combat_damage_to_player(attacker, defending_player, amount=trample_dmg)

        victim.damage_counter += dmg

        # ToDo: triggered abilities

    def deal_combat_damage_to_player(
        self, attacker: Creature, player: Player, amount: int | None = None
    ) -> None:
        """Attacker deals damage to the victim."""

        # ToDo: toxic
        # ToDo: infect

        if amount is None:
            player.life -= attacker.get_power()

        # damage is not None 
        else: 
            player.life -= amount
        
        # ToDo: triggered abilities

    def assign_combat_damage(self, attacker: Creature, blocker: list[Creature]) -> None:
        """Assign combat damage among defending creatures."""
        dmg_left = attacker.get_power()

        for victim in blocker:

            # creatures cannot deal damage or be dealt damage if they are removed from the field
            if victim not in self.reactive_player.creatures:
                continue

            # deal damage to attacking creature
            self.deal_combat_damage_to_creature(
                victim, attacker, self.reactive_player, self.active_player,
            )

            # if attacking creature can only assign damage equal to its power
            if dmg_left <= 0:
                continue
            
            # determine how much damage the attacker deals to this specific blocker
            dmg = self.active_player.choose_int_value(dmg_left)
            dmg_left = max(dmg - dmg_left, 0)
            self.deal_combat_damage_to_creature(
                attacker, victim, self.active_player, self.reactive_player, amount=dmg,
            )

    def damage_step(self, all_attacker: dict[Creature, list[Creature]]) -> None:
        """Deal combat damage to creatures and players. See concepts/Turn.md for more info."""

        for attacker, blocker in all_attacker.items():

            # no camage assignment if the attacking creature left the battlefield
            if attacker not in self.active_player.creatures:
                continue

            # no blocker: deal damage to opponent
            if len(blocker) == 0:
                self.deal_combat_damage_to_player(attacker, self.reactive_player)

            # only one blocker, full damage assignment to blocking creature.
            elif len(blocker) == 1:
                if blocker[0] in self.reactive_player.creatures:
                    self.deal_combat_damage_to_creature(attacker, blocker[0], self.active_player, self.reactive_player)
                    self.deal_combat_damage_to_creature(blocker[0], attacker, self.reactive_player, self.active_player)
            
            # multiple blocker, damage needs to be assigned by the player.
            elif len(blocker) > 1:
                self.assign_combat_damage(attacker, blocker)

        self.state_based_actions()
        self.priority(sorcery_speed=False)

    def end_of_combat_step(self) -> None:
        """Play end of combat step. See concepts/Turn.md for more info."""
        print("[END OF COMBAT STEP]")

        self.priority(sorcery_speed=False)

    def combat_phase(self) -> None:
        """Play a whole combat phase. See concepts/Turn.md for more info."""
        self.beginning_of_combat_step()
        attacker = self.declare_attacker_step()
        attacker = self.declare_blocker_step(attacker)
        # ToDo: first-strike
        self.damage_step(attacker)
        self.end_of_combat_step()
        self.clear_player_mana()


    # END PHASE


    def beginning_of_end_phase_step(self) -> None:
        """Play the beggning of the end phase."""
        print("[BEGINNING OF END PHASE]")

        # ToDo: triggered abilities

        pass

    def end_step(self) -> None:
        """Play the end phase of this turn."""
        print("[END STEP]")

        self.priority(sorcery_speed=False)

    def cleanup_step(self) -> None:
        """Play the cleanup step of this turn.
        - remove damage counter from creatures.
        """
        print("[CLEANUP STEP]")

        # remove damage countes from creatures
        for p in [self.p1, self.p2]:
            for creature in p.creatures:
                creature.damage_counter = 0

            # remove floating mana
            p.clear_floating_mana()

            # remove until-end-of-turn effects
            for eot in p.eot_effects:
                if isinstance(eot, Modifier):

                    # only one target
                    if isinstance(eot.target, Card):
                        eot.target.modifiers.remove(eot)

                    # multiple targets
                    if isinstance(eot.target, list):
                        for target in eot.target:
                            target.modifiers.remove(eot)
                    
                    p.eot_effects.remove(eot)
                    del eot

        # discard due to handsize
        while len(self.active_player.hand) > 7:
            print("Discard due to handsize.")
            card = self.active_player.target(own_hand=True)
            self.active_player.discard_one_card(card)

    def end_phase(self) -> None:
        """Play a whole end phase."""
        self.beginning_of_end_phase_step()
        self.end_step()
        self.cleanup_step()
        self.clear_player_mana()


    # HELPER FUNCTIONS
    

    def state_based_actions(self) -> None:
        """Perform state based actions on this game. Only player life and creature dmg for now."""
        loosers = []
        for player in [self.p1, self.p2]:

            # player lost
            if player.life <= 0:
                loosers.append(player)

            # damage counter
            for creature in player.creatures:
                if creature.damage_counter >= creature.get_toughness():
                    print(f"[STATE BASED ACTIONS] {creature.name} dies due to damage.")
                    player.send_creature_from_field_to_graveyard(creature)

        # end game
        if len(loosers) == 1:
            winner = self.p1 if self.p1 not in loosers else self.p2
            raise Exception(winner.name)
        if len(loosers) == 2:
            raise Exception("Draw")


    def play_land(self, data: PriorityData, card: Land) -> None:
        """Play a land."""
        # 1. Announce playing the land.
        # ToDo: Playing from graveyard or exile (zone other than hand)
        # ToDo: Double-sided (mdfc)

        # 2. Immediate ETB
        # ToDo: replacement effects (e.g. enters tapped)

        data.priority_player.lands.append(card)
        data.priority_player.hand.remove(card)

        # 3. Increment played lands counter
        
        self.hit_landdrop = True

        # 4. Land was played successfully
        # ToDo: Landfall

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
        """Activate an ability. For more info, look at 'concepts/Cast_or_Activate.md'."""

        # 1. Announce activating an ability.
        # ToDo: cards with multiple activated abilities

        # 2. Making decisions
        # ToDo: modus

        # 5. Legality check
        # Move to front to avoid having to revert and debug ridiculous boardstates

        if not card.activated_ability.can_activate(
            card, data.priority_player, data.non_priority_player
        ):
            return

        # 6. Determine total cost
        
        cost = card.activated_ability.mana_cost

        # 7. Use mana-abilities
        # 8. Pay the cost
        # Move to fron to avoid having to revert and debug ridiculous boardstates

        # ToDo: add check if enough mana can be produced to pay for this Ability
        # ToDo: split creating mana and paying mana in 2 functions
        # ToDo: make make mana payment more efficient

        if (
            cost is not None
            and not data.priority_player.pay_for_manacost(cost, data.non_priority_player)
        ):
            return

        card.activated_ability.pay_cost(card, data.priority_player, data.non_priority_player)

            # 3. Choosing targets

        card.activated_ability.choose_targets(card, data.priority_player, data.non_priority_player)

        # 4. Determine distribution
        
        # 1. again - put ability on the stack
        # excep mana abilities: resolve them instantly.
        # Move to end to avoid having to revert and debug ridiculous boardstates
        
        if card.activated_ability.is_mana_ability:
            card.activated_ability.activity(
                card, data.priority_player, data.non_priority_player,
            )
        # non-mana ability
        else:
            self.put_action_on_stack(data, "Ability", card)

        # 9. Ability was activated successfully
        # ToDo: triggered abilities        

    def cast_spell(self, data: PriorityData, card: Card) -> None:
        """Cast a spell. For more info, look at 'concepts/Cast_or_Activate.md'."""
        
        # 1. Announce casting a spell
        # ToDo: casting from graveyard or exile (zone other than hand)
        # ToDo: Double-sided (mdfc)
        # ToDo: multi- & split-cards (fire//ice)

        # 2. Making decisions
        # ToDo: modus
        # ToDo: alternate and/or additional cost
        # ToDo: variable cost (X)
        # ToDo: splice onto

        # 5. Legality check
        # Move to front to avoid having to revert and debug ridiculous boardstates
        # Hope legal action generation helps
        # ToDo: add quick check if enough mana exists to pay for cost

        if (
            isinstance(card, (Instant, Sorcery)) 
            and not card.ability.can_activate(
                card, data.priority_player, data.non_priority_player
            )
        ):
            return

        # 3. Choosing targets
        # ToDo: creatures that target on cast
        # ToDo: keywords (Aura)

        if isinstance(card, (Instant, Sorcery)):
            card.ability.choose_targets(card, data.priority_player, data.non_priority_player)

        # 4. Determine distribution

        # 6. Determine total cost
        # ToDo: Affinity

        cost = card.cost

        # 7. Use mana-abilities
        # 8. Pay the cost
        # ToDo: split creating mana and paying mana in 2 functions

        if not data.priority_player.pay_for_manacost(cost, data.non_priority_player):
            return

        if isinstance(card, (Instant, Sorcery)):
            card.ability.pay_cost(card, data.priority_player, data.non_priority_player)

        # 1. again - put spell on the stack
        # Move to end to avoid having to revert and debug ridiculous boardstates

        data.priority_player.hand.remove(card)
        self.put_action_on_stack(data, "Cast", card)

        # 9. spell is cast successfully
        # ToDo: triggered abilities
        # ToDo: Cascade

    def swap_priority(self, data: PriorityData) -> None:
        """On 2 or less passes, non_active_player receives priority. Otherwise, resolve the next item on the stack."""
        self.state_based_actions()
        # single pass: give priority to opponent
        if data.pass_counter < 2:
            data.swap_priority()
            # goto 5.
            data.state = "Action"
            return
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
        #print(f"[RESOLVE] resolving {"Ability" if action == "Ability" else "Cast"} of {card.name}")

        # resolve Casting Spells
        if stack_object.action == "Cast":
            # Creature -> put it on the field
            if isinstance(card, Creature):
                owner.creatures.append(card)
                # ToDo: etb
                
            # Sorceries or Instants -> resolve abilities
            if isinstance(card, (Instant, Sorcery)):
                card.ability.activity(card, owner, opponent)
                owner.graveyard.append(card)
        
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

                # Passing
                if action == "Pass":
                    self.priority_pass(data)

                # Playing Lands
                if action == "Play" and isinstance(card, Land):
                    self.play_land(data, card)

                # Activate Abilities (including mana abilities)
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
