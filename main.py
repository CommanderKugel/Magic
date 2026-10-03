from pathlib import Path
from copy import deepcopy
import traceback

from src.Magic.Game import Game
from src.Player.CLIPlayer import CLIPlayer
from src.Player.RandomPlayer import RandomPlayer
from src.Magic.Library import load_from_decklist, shuffle, seed_players_cards
from src.implementation.cards import get_card

# "Balduvian_Bears"

bear_list_path = Path(__file__).resolve().parent / "resources/bear_list.txt"
bolt_list_path = Path(__file__).resolve().parent / "resources/bolt_list.txt"

results = []
for i in range(100):
    p1 = RandomPlayer("P1", 20, load_from_decklist(bear_list_path, get_card))
    p2 = RandomPlayer("P2", 20, load_from_decklist(bear_list_path, get_card))
    game = Game(p1, p2)
    game.prepare_game()
    try:
        while True:
            game.play_turn()
    except Exception as e:
        print(f"[{i}] - {game.turn} turns. result={e}")
        results.append((e, game.turn))

        if e.args[0] not in [p1.name, p2.name]:
            traceback.print_exc()
            break

print(f"total games: {len(results)} avg: {sum(t for _, t in results) / len(results)} turns")
