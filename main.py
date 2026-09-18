from Magic.Game import Game
from Magic.Player import Player
from Magic.Library import get_dummy_lib

p1 = Player(20, get_dummy_lib())
p2 = Player(20, get_dummy_lib())

game = Game(p1, p2)
game.prepare()
game.play_turn()
