import sys
import pygame as pg
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Player.Player import Player
from Magic.Game import Game
from Magic.Library import get_dummy_lib

from Pygame.Board import draw_game, load_card_images


screen = pg.display.set_mode((1800, 1200))
clock = pg.time.Clock()


def main_loop(game: Game):
    while True:
        screen.fill((60, 60, 90))
        draw_game(game, screen)
        pg.display.flip()

        for event in pg.event.get():
            if (
                event.type == pg.QUIT
                or event.type == pg.KEYDOWN
            ):
                pg.quit()
                sys.exit()
        clock.tick(60)

        game.play_turn()

if __name__ == "__main__":
    game = Game(
        Player(20, get_dummy_lib()), 
        Player(20, get_dummy_lib())
    )
    load_card_images(game.p1.library)
    load_card_images(game.p2.library)
    game.prepare()
    main_loop(game)
