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
        activated_ability=src.implementation.abilities.LandTapForGreen,
    ),

    "Mountain": Land(
        name="Mountain", 
        color=["None"], 
        mana_color="Red",
        activated_ability=src.implementation.abilities.LandTapForRed,
    ),

    "Balduvian_Bears": Creature(
        name="Balduvian_Bears",
        subtype=["Beast"],
        color=["Green"],
        cost={"Green": 1, "None": 1},
        base_power=2,
        base_toughness=2,
    ),

    "Llanowar_Elves": Creature(
        name="Llanowar Elves",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost={"Green": 1},
        base_power=1,
        base_toughness=1,
        activated_ability=src.implementation.abilities.CreatureTapForGreen,
    ),

    "Priest_of_Titania": Creature(
        name="Priest of Titania",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost={"Green": 1, "None": 1},
        base_power=1,
        base_toughness=1,
        activated_ability=src.implementation.abilities.PriestOfTitania,
    ),

    "Fyndhorn_Elves": Creature(
        name="Fyndhorn Elves",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost={"Green": 1},
        base_power=1,
        base_toughness=1,
        activated_ability=src.implementation.abilities.CreatureTapForGreen,
    ),

    "Timberwatch_Elf": Creature(
        name="Timberwatch Elf",
        subtype=["Elf"],
        color=["Green"],
        cost={"Green": 1, "None": 2},
        base_power=1,
        base_toughness=2,
        activated_ability=src.implementation.abilities.TimberwatchElf,
    ),

    "Almighty_Brushwagg": Creature(
        name="Almighty Brushwagg",
        subtype=["Brushwagg"],
        color=["Green"],
        cost={"Green": 1},
        base_power=1,
        base_toughness=1,
        _trample=True,
        activated_ability=src.implementation.abilities.AlmightyBrushwagg,
    ),

    "Colossal_Dreadmaw": Creature(
        name="Colossal Dreadmaw",
        subtype=["Dinsaur"],
        color=["Green"],
        cost={"Green": 2, "None": 4},
        base_power=6,
        base_toughness=6,
        _trample=True,
    ),

    "Storm_Crow": Creature(
        name="Storm Crow",
        subtype=["Bird"],
        color=["Blue"],
        cost={"Blue": 1, "None": 1},
        base_power=1,
        base_toughness=2,
        _flying=True,
    ),

    "Horrific_Assault": Sorcery(
        name="Horrific Assault",
        ability=src.implementation.abilities.Punch,
        color=["Green"],
        cost={"Green": 1},
    ),

    "Lightning_Bolt": Instant(
        name="Lightbing Bolt",
        ability=src.implementation.abilities.Bolt,
        color=["Red"],
        cost={"Red": 1},
    ),

    "Blitzball_Shot": Instant(
        name="Blitzball Shot",
        ability=src.implementation.abilities.BlitzBallShot,
        color=["Green"],
        cost={"Green": 1, "None": 1},
    ),

    "Giant_Growth": Instant(
        name="Giant Growth",
        ability=src.implementation.abilities.GiantGrowth,
        color=["Green"],
        cost={"Green": 1},
    )
}

for key, card in _ALL_CARDS.items():
    if isinstance(card, Creature):
        card.modifiers = []
