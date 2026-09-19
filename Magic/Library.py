from random import shuffle
from pathlib import Path

from Magic.Card import Card

def shuffle_library(lib: list[Card]) -> None:
    """Shuffle the library in-place."""
    shuffle(lib)

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
            deck.extend([all_cards[card_name] for _ in range(amount)])
    return deck
