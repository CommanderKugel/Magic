from pathlib import Path
from copy import deepcopy

from Magic.Game import Game
from Player.CLIPlayer import CLIPlayer
from Player.RandomPlayer import RandomPlayer
from Magic.Library import load_from_decklist, shuffle, seed_players_cards
from implementation.cards import get_card

# "Balduvian_Bears"

bear_list_path = Path(__file__).resolve().parent / "resources/bolt_list.txt"
bolt_list_path = Path(__file__).resolve().parent / "resources/bolt_list.txt"

p1 = CLIPlayer("P1", 20, load_from_decklist(bolt_list_path, get_card))
p2 = CLIPlayer("P2", 20, load_from_decklist(bolt_list_path, get_card))
game = Game(p1, p2)

p2.creatures = [get_card("Balduvian_Bears")]
p2.lands = [get_card("Forest")]
p2.hand = [get_card("Giant_Growth")]

game.prepare_turn()

while True:
    game.play_turn()
