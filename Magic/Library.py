from dataclasses import dataclass
from random import shuffle

from Magic.Card import Card, Bear, Forest

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

def get_dummy_lib() -> list[Card]:
    """Prepare a super basic 40 card deck with bears and forests."""
    return (
        [Bear for _ in range(24)] 
        + [Forest for _ in range(16)]
    )
