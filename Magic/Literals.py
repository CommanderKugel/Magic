from typing import Literal


Action = Literal[
    "Pass",
    "Play",
    "Cast",
    "Ability",
]

Color = Literal[
    "White",
    "Blue",
    "Black",
    "Red",
    "Green",
    "None",
]

CardType = Literal[
    "Basic Land",
    "Creature",
    "Sorcery",
    "Instant",
]