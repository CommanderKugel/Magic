from Magic.Player import Player
from Magic.Card import Card, Creature, Land
from Magic.Library import shuffle_library

# for now only 2 players

class Game:
    def __init__(self, p1: Player, p2: Player):
        self.p1 = p1
        self.p2 = p2
        
        self.turn = 0
        self.active_player = None

        self.step = None
        self.hit_landdrop = False

        self.stack: list[Card] = []

    def __repr__(self):
        return (
            f"[OPP LAND]      {[c.name for c in self.reactiva_player.lands]}\n"
            f"[OPP CREATURES] {[c.name for c in self.reactiva_player.creatures]}\n"
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
        self.reactiva_player = self.p2 if self.turn % 2 else self.p1
        self.hit_landdrop = False

        self.beginning_phase()
        self.main_phase()
        self.combat_phase()
        self.main_phase()
        self.end_phase()

    def clear_player_mana(self) -> None:
        """Clear all players floating mana."""
        self.p1.clear_floating_mana()
        self.p2.clear_floating_mana()
    
    def beginning_phase(self) -> None:
        """Play the whole beginning phase of this turn."""

        def untap_step():
            """Play the untap step."""
            print("[UNTAP]")
            self.step = "Untap"
            # ToDo: Priority

            for creature in self.active_player.creatures:
                creature.tapped = False
            for land in self.active_player.lands:
                land.tapped = False

        def upkeep_step():
            """Play the Upkeep step."""
            print("[UPKEEP]")
            self.step = "Upkeep"
            # ToDo: Priority

        def draw_step():
            """Play the Draw step."""
            print("[DRAW]")
            self.step = "Draw"
            # ToDo: Priority
            self.active_player.draw(1)
        
        untap_step()
        upkeep_step()
        draw_step()
        self.clear_player_mana()
    
    def main_phase(self) -> None:
        """Play a whole main phase. There are two per turn, most of the time."""
        print("[MAIN PHASE]")
        self.step = "Main"
        
        while True:
            print(self)

            # ToDo: put actions on stack and pass priority around.
            # ToDo: instantly play Lands, no reaction possible there.
            action, source = self.active_player.choose_action_dummy(
                hit_landdrop=self.hit_landdrop,
            )

            # passing
            if action == "Pass":
                print("Passed during main phase.")
                break

            # ToDo: Replace the next code with the stack.
            #       We instantly resolve actions for now.
            
            # play a land
            if action == "Play":
                if self.hit_landdrop:
                    print("Already hit your landdrop this turn, illegal action.")
                    continue
                print("Playing Land:", source.name)
                self.active_player.play_land_from_hand(source)
                self.hit_landdrop = True
                
            elif action == "Cast":
                print("Attempting to cast spell:", source.name)
                self.active_player.play_creature_from_hand(source)

            elif action == "Ability":
                print("Activating ability:", Card(source).name)
                ability = source.activated_ability
                if not ability.can_activate(source, self.active_player):
                    print("Activating unactivatable abilities is illegal.")
                    continue
                ability.pay_cost(source, self.active_player)
                ability.activity(source, self.active_player)

            # end of "replace this code with the stack" block
        self.clear_player_mana()

    def combat_phase(self) -> None:
        """Play a whole combat phase."""

        def beginning_of_combat() -> None:
            """Play beginning of combat step."""
            print("[BEGINNING OF COMBAT]")
            self.step = "BeginningOfCombat"
            # ToDo: triggered abilities
            # ToDo: priority

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
            # ToDo: priority
            return attacker

        def declare_blockers(attacker: dict[Creature, list[Creature]]) -> dict[Creature, list[Creature]]:
            """Declare blocker to this turns attackers."""
            print("[DECLARE BLOCKERS STEP]")
            self.step = "DeclareBlocker"
            available_blocker = [c for c in self.reactiva_player.creatures]
            for att in attacker.keys():
                for blocker in available_blocker:
                    if self.reactiva_player.binary_choice(
                        f"Do you want to block {att.name} with {blocker.name}?"
                    ):
                        attacker[att].append(blocker)
                        available_blocker.remove(blocker)
            # ToDo: Priority
            return attacker

        def damage_step(attacker_: dict[Creature, list[Creature]]) -> None:
            """Deal combat damage to creatures and players."""
            print("[DAMAGE STEP]")
            self.step = "Damage"

            for attacker, blocker in attacker_.items():
                # no blocker: deal damage to opponent
                if len(blocker) == 0:
                    self.reactiva_player.life -= attacker.power
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
            # ToDo: priority

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
            # ToDo: priority
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

