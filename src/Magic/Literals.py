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

PriorityState = Literal[
    "Action",
    "Passing",
    "Resolve",
]
