from pathlib import Path
from copy import deepcopy

from Magic.Game import Game
from Player.CLIPlayer import CLIPlayer
from Magic.Library import load_from_decklist, shuffle
from implementation.cards import ALL_CARDS

list_path = Path(__file__).resolve().parent / "resources/dummy_list.txt"

p1 = CLIPlayer(20, load_from_decklist(list_path, ALL_CARDS))
p2 = CLIPlayer(20, load_from_decklist(list_path, ALL_CARDS))

p1.name = "P1"
p2.name = "P2"

game = Game(p1, p2)
shuffle(game.p1.library)
shuffle(game.p2.library)

game.p1.creatures.append(deepcopy(ALL_CARDS["Balduvian_Bears"]))
game.p2.creatures.append(deepcopy(ALL_CARDS["Balduvian_Bears"]))

game.p1.hand.append(deepcopy(ALL_CARDS["Horrific_Assault"]))
game.p2.hand.append(deepcopy(ALL_CARDS["Horrific_Assault"]))

game.p1.hand.append(deepcopy(ALL_CARDS["Forest"]))
game.p2.hand.append(deepcopy(ALL_CARDS["Forest"]))

game.play_turn()
