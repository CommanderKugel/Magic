from pathlib import Path
from copy import deepcopy

from Magic.Game import Game
from Player.CLIPlayer import CLIPlayer
from Player.RandomPlayer import RandomPlayer
from Magic.Library import load_from_decklist, shuffle, seed_players_cards
from implementation.cards import get_card

bear_list_path = Path(__file__).resolve().parent / "resources/bolt_list.txt"
bolt_list_path = Path(__file__).resolve().parent / "resources/bolt_list.txt"

def run():
    p1 = RandomPlayer("P1", 20, load_from_decklist(bolt_list_path, get_card))
    p2 = RandomPlayer("P2", 20, load_from_decklist(bolt_list_path, get_card))
    game = Game(p1, p2)

    game.prepare_game()

    print("=" * 20, "PLAY NEW GAME", "=" * 20)
    try:
        import time
        start_time = time.time_ns()
        while True:
            game.play_turn()
    except Exception as e:
        end_time = time.time_ns()
        winner = e.args[0]
        print("[ERROR]", e)
    return winner, end_time - start_time

results = [
    run()
    for _ in range(10)
]

for winner, time in results:
    print(f"winner: {winner}, time: {time}")