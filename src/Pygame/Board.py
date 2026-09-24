import pygame as pg
from pathlib import Path

from src.Magic.Game import Game
from src.Magic.Card import Card

PROJECT_ROOT = Path(__file__).parent.parent
CARD_DIR = PROJECT_ROOT / "resources"

IMAGES = {}
IMAGE_WIDTH = 207
IMAGE_HEIGHT = 290
ZONE_HEIGHT = 300

def draw_game(game: Game, screen: pg.Surface):
    """Draw game on pygame screen."""

    pg.draw.line(screen, "black", (0, 300), (1800, 300), width=2)
    pg.draw.line(screen, "black", (0, 600), (1800, 600), width=2)
    pg.draw.line(screen, "black", (0, 900), (1800, 900), width=2)

    for zone, l in enumerate([
        game.p2.hand,
        game.p2.creatures,
        game.p1.creatures,
        game.p1.hand,
    ]):
        for idx, card in enumerate(l):
            x = idx * (IMAGE_WIDTH + 5)
            y = ZONE_HEIGHT * zone + 5
            img = IMAGES[card.name]
            screen.blit(img, (x, y))


def load_card_images(lib: list[Card]):
    """Loads and caches all unique card images from the given library."""
    for card in lib:
        if card.name not in IMAGES:
            img = pg.image.load(CARD_DIR / card.image).convert()
            img = pg.transform.scale(img, (IMAGE_WIDTH, IMAGE_HEIGHT))
            IMAGES[card.name] = img
            print("Loaded", card.image)

