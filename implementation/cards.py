from Magic.Card import Land, Creature
from implementation.abilities import TapForGreen

ALL_CARDS = {
    "Forest": Land(
        name="Forest", 
        color=["None"], 
        type="Basic Land", 
        mana_color="Green",
        tapped=False,
        image="Forest.png",
    ),

    "Balduvian_Bears": Creature(
        name="Balduvian_Bears",
        type="Creature",
        subtype="Beast",
        color=["Green"],
        cost={"Green": 2},
        power=2,
        toughness=2,
        tapped=False,
        image="Balduvian_Bears.png",
    ),
}