from pathlib import Path

from Magic.Game import Game
from Magic.Player import Player
from Magic.Library import load_from_decklist
from implementation.cards import ALL_CARDS

list_path = Path(__file__).resolve().parent / "resources/dummy_list.txt"

p1 = Player(20, load_from_decklist(list_path, ALL_CARDS))
p2 = Player(20, load_from_decklist(list_path, ALL_CARDS))

game = Game(p1, p2)
game.prepare()
bear = ALL_CARDS["Balduvian_Bears"]
game.p1.creatures.append(bear)
game.p2.creatures.append(bear)

try:
    while True:
        game.play_turn()
except:
    print("game ended.")
