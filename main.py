from pathlib import Path

from Magic.Game import Game
from Player.CLIPlayer import CLIPlayer
from Magic.Library import load_from_decklist
from implementation.cards import ALL_CARDS

list_path = Path(__file__).resolve().parent / "resources/dummy_list.txt"

p1 = CLIPlayer(20, load_from_decklist(list_path, ALL_CARDS))
p2 = CLIPlayer(20, load_from_decklist(list_path, ALL_CARDS))

p1.name = "P1"
p2.name = "P2"

game = Game(p1, p2)
game.prepare()

game.turn += 1
game.active_player = game.p1 if game.turn % 2 else game.p2
game.reactive_player = game.p2 if game.turn % 2 else game.p1
game.hit_landdrop = game

game.play_turn()

