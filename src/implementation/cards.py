import copy
import uuid
import src.implementation.abilities

from src.Magic.Card import Card, Land, Creature, Sorcery, Instant


def get_card(name: str) -> Card:
    """Fetch copy of a card by name."""
    card = _ALL_CARDS.get(name, None)
    if card is None:
        raise ValueError(f"Card name '{name}' does not exist.")
    card = copy.deepcopy(card)
    card.id = str(uuid.uuid1())
    return card

_ALL_CARDS = {
    "Forest": Land(
        name="Forest", 
        color=["None"], 
        mana_color="Green",
        tapped=False,
        image="Forest.png",
        activated_ability=src.implementation.abilities.TapForGreen,
    ),

    "Mountain": Land(
        name="Mountain", 
        color=["None"], 
        mana_color="Red",
        tapped=False,
        image="Mountain.png",
        activated_ability=src.implementation.abilities.TapForRed,
    ),

    "Balduvian_Bears": Creature(
        name="Balduvian_Bears",
        subtype="Beast",
        color=["Green"],
        cost={"Green": 1, "None": 1},
        base_power=2,
        base_toughness=2,
        tapped=False,
        image="Balduvian_Bears.png",
    ),

    "Horrific_Assault": Sorcery(
        name="Horrific Assault",
        ability=src.implementation.abilities.Punch,
        color=["Green"],
        cost={"Green": 1},
        image="Horrific_Assault.png",
    ),

    "Lightning_Bolt": Instant(
        name="Lightbing Bolt",
        ability=src.implementation.abilities.Bolt,
        color=["Red"],
        cost={"Red": 1},
        image="Lightning_Bolt.png",
    ),

    "Giant_Growth": Instant(
        name="Giant Growth",
        ability=src.implementation.abilities.GiantGrowth,
        color=["Green"],
        cost={"Green": 1},
        image="",
    )
}

for key, card in _ALL_CARDS.items():
    if isinstance(card, Creature):
        card.buffs = []
