from uuid import uuid1
from random import shuffle
from pathlib import Path
from typing import Callable

from src.Magic.Card import Card, Creature

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
    """Removes Top Card from library (in-place) and returns it. Return None, if the library is empty."""
    if len(lib) == 0:
        return None
    return lib.pop(0)

def get_top_n_cards(n: int, lib: list[Card]) -> list[Card]:
    """Remove the top n cards from library and return them as a list."""
    n = min(n, len(lib))
    bunch = lib[:n]
    del lib[:n]
    return bunch

def put_under_library_in_random_order(cards: list[Card], lib: list[Card]):
    """Puts the cards under the library in a random order."""
    shuffle(cards)
    lib.extend(cards)

def tutor_card(name: str, lib: list[Card]) -> Card | None:
    """Tutors card from the library. Returns None when failed to find."""
    for card in lib:
        if card.name == name:
            lib.remove(card)
            return card
    return None

def load_from_decklist(decklist: str | Path, get_card: Callable) -> list[Card]:
    """Load deck from a decklist."""
    deck: list[Card] = []
    with open(decklist, "r") as f:
        for line in f.readlines():
            content = line.split(" ")
            amount = int(content[0])
            card_name = content[1].strip()
            deck.extend([
                get_card(card_name) 
                for _ in range(amount)
            ])
    for card in deck:
        card.id = str(uuid1())
    return deck
