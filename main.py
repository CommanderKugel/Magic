from pathlib import Path
from copy import deepcopy

from Magic.Game import Game
from Player.CLIPlayer import CLIPlayer
from Magic.Library import load_from_decklist, shuffle, seed_players_cards
from implementation.cards import get_card

list_path = Path(__file__).resolve().parent / "resources/dummy_list.txt"

p1 = CLIPlayer(20, load_from_decklist(list_path, get_card))
p2 = CLIPlayer(20, load_from_decklist(list_path, get_card))

p1.name = "P1"
p2.name = "P2"

game = Game(p1, p2)
shuffle(game.p1.library)
shuffle(game.p2.library)

game.p1.creatures = [get_card("Balduvian_Bears")]
game.p2.creatures = [get_card("Balduvian_Bears")]

game.p1.hand = [
    get_card("Lightning_Bolt"),
    get_card("Balduvian_Bears"),
    get_card("Mountain"),
    get_card("Forest"),
    get_card("Forest"),
]

seed_players_cards(p1)
seed_players_cards(p2)

game.p1.floating_mana["Green"] = 2
game.p1.floating_mana["Red"] = 1

game.prepare_turn()
game.main_phase()
