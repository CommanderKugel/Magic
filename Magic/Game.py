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
            f"[HAND]      {["X" for _ in self.p2.hand]}\n"
            f"[LAND]      {[c.name for c in self.p2.lands]}\n"
            f"[CREATURES] {[c.name for c in self.p2.creatures]}\n"
            f"[CREATURES] {[c.name for c in self.p1.creatures]}\n"
            f"[LAND]      {[c.name for c in self.p1.lands]}\n"
            f"[HAND]      {[c.name for c in self.p1.hand]}\n"
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
        self.hit_landdrop = False

        self.beginning_phase()
        self.main_phase()
    
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
    
    def main_phase(self) -> None:
        """Play a whole main phase. There are two per turn, most of the time."""
        self.step = "Main"
        
        while True:
            print(self)

            # ToDo: put actions on stack and pass priority around.
            # ToDo: instantly play Lands, no reaction possible there.
            action = self.active_player.choose_action_dummy(
                hit_landdrop=self.hit_landdrop,
            )

            # passing
            if action is None:
                break

            # ToDo: Replace the next code with the stack.
            #       We instantly resolve actions for now.

            if isinstance(action, Land):
                if self.hit_landdrop:
                    print("Already hit your landdrop this turn, what happened?")
                    continue
                self.active_player.play_land_from_hand(action)
                self.hit_landdrop = True
                
            elif isinstance(action, Creature):
                self.active_player.play_creature_from_hand(action)

            # end of "replace this code with the stack" block

