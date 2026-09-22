from uuid import uuid1
from random import shuffle
from pathlib import Path
from copy import deepcopy
from typing import Callable

from Magic.Card import Card

def shuffle_library(lib: list[Card]) -> None:
    """Shuffle the library in-place."""
    shuffle(lib)

def seed_list(l: list[Card]) -> None:
    """Give list of cards IDs."""
    for card in l:
        card.id = str(uuid1())

def seed_players_cards(p) -> None:
    """Give all cards a player controls IDs. p is an instance of Player."""
    for l in [
        p.hand, p.lands, p.creatures, p.library, p.graveyard
    ]:
        seed_list(l)

def draw_card(lib: list[Card]) -> Card | None:
    """Removes Top Card from library (in-place) and returns it.
    
    Return None, if the library is empty.
    """
    if len(lib) == 0:
        return None
    return lib.pop(0)

def load_from_decklist(decklist: str | Path, all_cards: dict[str, Card]) -> list[Card]:
    """Load deck from a decklist."""
    deck: list[Card] = []
    with open(decklist, "r") as f:
        for line in f.readlines():
            content = line.split(" ")
            amount = int(content[0])
            card_name = content[1].strip()
            deck.extend([
                deepcopy(all_cards[card_name]) 
                for _ in range(amount)
            ])
    for card in deck:
        card.id = str(uuid1())
    return deck
