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
        image="Forest.png",
        activated_ability=src.implementation.abilities.LandTapForGreen,
    ),

    "Mountain": Land(
        name="Mountain", 
        color=["None"], 
        mana_color="Red",
        image="Mountain.png",
        activated_ability=src.implementation.abilities.LandTapForRed,
    ),

    "Balduvian_Bears": Creature(
        name="Balduvian_Bears",
        subtype=["Beast"],
        color=["Green"],
        cost={"Green": 1, "None": 1},
        base_power=2,
        base_toughness=2,
        image="Balduvian_Bears.png",
    ),

    "Llanowar_Elves": Creature(
        name="Llanowar Elves",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost={"Green": 1},
        base_power=1,
        base_toughness=1,
        image="Llanowar_Elves.png",
        activated_ability=src.implementation.abilities.CreatureTapForGreen,
    ),

    "Priest_of_Titania": Creature(
        name="Priest of Titania",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost={"Green": 1, "None": 1},
        base_power=1,
        base_toughness=1,
        image="Priest_of_Titania.png",
        activated_ability=src.implementation.abilities.PriestOfTitania,
    ),

    "Fyndhorn_Elves": Creature(
        name="Fyndhorn Elves",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost={"Green": 1},
        base_power=1,
        base_toughness=1,
        image="Fyndhorn_Elves.png",
        activated_ability=src.implementation.abilities.CreatureTapForGreen,
    ),

    "Timberwatch_Elf": Creature(
        name="Timberwatch Elf",
        subtype=["Elf"],
        color=["Green"],
        cost={"Green": 1, "None": 2},
        base_power=1,
        base_toughness=2,
        image="Timberwatch_Elf.png",
        activated_ability=src.implementation.abilities.TimberwatchElf,
    ),

    "Colossal_Dreadmaw": Creature(
        name="Colossal Dreadmaw",
        subtype=["Dinsaur"],
        color=["Green"],
        cost={"Green": 2, "None": 4},
        base_power=6,
        base_toughness=6,
        image="Colossal_Dreadmaw.png",
        trample=True,
    ),

    "Storm_Crow": Creature(
        name="Storm Crow",
        subtype=["Bird"],
        color=["Blue"],
        cost={"Blue": 1, "None": 1},
        base_power=1,
        base_toughness=2,
        image="Storm_Crow.png",
        flying=True,
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
