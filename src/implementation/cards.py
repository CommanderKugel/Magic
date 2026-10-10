import copy
import uuid
import src.implementation.abilities as abilities

from src.Magic.Card import Card, Land, Artifact, Creature, Sorcery, Instant
from src.Magic.Cost import Cost


def get_card(name: str, source: dict | None = None) -> Card:
    """Fetch copy of a card by name."""
    if source is None:
        source = _ALL_CARDS
    card = source.get(name, None)
    if card is None:
        raise ValueError(f"Card name '{name}' does not exist.")
    card = copy.deepcopy(card)
    card.id = str(uuid.uuid1())
    return card

_ALL_CARDS = {

    # BASICS

    "Forest": Land(
        name="Forest", 
        color=["None"], 
        mana_color="Green",
        activated_ability=abilities.LandTapForGreen,
    ),

    "Mountain": Land(
        name="Mountain", 
        color=["None"], 
        mana_color="Red",
        activated_ability=abilities.LandTapForRed,
    ),

    # TEST CARDS

    "Balduvian_Bears": Creature(
        name="Balduvian_Bears",
        subtype=["Beast"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1, "None": 1}),
        base_power=2,
        base_toughness=2,
    ),

    "Almighty_Brushwagg": Creature(
        name="Almighty Brushwagg",
        subtype=["Brushwagg"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1}),
        base_power=1,
        base_toughness=1,
        _trample=True,
        activated_ability=abilities.AlmightyBrushwagg,
    ),

    "Colossal_Dreadmaw": Creature(
        name="Colossal Dreadmaw",
        subtype=["Dinsaur"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 2, "None": 4}),
        base_power=6,
        base_toughness=6,
        _trample=True,
    ),

    "Storm_Crow": Creature(
        name="Storm Crow",
        subtype=["Bird"],
        color=["Blue"],
        cost=Cost(mana_cost={"Blue": 1, "None": 1}),
        base_power=1,
        base_toughness=2,
        _flying=True,
    ),

    "Horrific_Assault": Sorcery(
        name="Horrific Assault",
        ability=abilities.Punch,
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1}),
    ),

    "Blitzball_Shot": Instant(
        name="Blitzball Shot",
        ability=abilities.BlitzBallShot,
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1, "None": 1}),
    ),

    "Giant_Growth": Instant(
        name="Giant Growth",
        ability=abilities.GiantGrowth,
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1}),
    ),

    "Spectral_Hunt-Caller": Creature(
        name="Spectral Hunt-Caller",
        subtype=["Wolf", "Spirit"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1, "None": 4}),
        base_power=4,
        base_toughness=4,
        activated_ability=abilities.SpectralHuntCaller,
    ),

    "Springleaf_Drum": Artifact(
        name="Springleaf Drum",
        activated_ability=abilities.SpringleafDrum,
        color=["None"],
        cost=Cost(mana_cost={"None": 1}),
    ),

    # ELVES

    "Llanowar_Elves": Creature(
        name="Llanowar Elves",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1}),
        base_power=1,
        base_toughness=1,
        activated_ability=abilities.CreatureTapForGreen,
    ),

    "Elvish_Mystic": Creature(
        name="Elvish Mystic",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1}),
        base_power=1,
        base_toughness=1,
        activated_ability=abilities.CreatureTapForGreen,
    ),

    "Fyndhorn_Elves": Creature(
        name="Fyndhorn Elves",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1}),
        base_power=1,
        base_toughness=1,
        activated_ability=abilities.CreatureTapForGreen,
    ),

    "Priest_of_Titania": Creature(
        name="Priest of Titania",
        subtype=["Elf", "Druid"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1, "None": 1}),
        base_power=1,
        base_toughness=1,
        activated_ability=abilities.PriestOfTitania,
    ),

    "Timberwatch_Elf": Creature(
        name="Timberwatch Elf",
        subtype=["Elf"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1, "None": 2}),
        base_power=1,
        base_toughness=2,
        activated_ability=abilities.TimberwatchElf,
    ),

    "Generous_Ent": Creature(
        name="Generous Ent",
        subtype=["Treefolk"],
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1, "None": 5}),
        base_power=5,
        base_toughness=7,
        _reach=True,
        activated_ability=abilities.ForestCycling,
        etb_ability=abilities.CreateFood,
    ),

    "Lead_the_Stampede": Sorcery(
        name="Lead the Stampede",
        ability=abilities.LeadTheStampede,
        color=["Green"],
        cost=Cost(mana_cost={"Green": 1, "None": 2}),
    ),

    # MADNESS

    "Voldaren_Epicure": Creature(
        name="Voldaren Epicure",
        subtype=["Vampire"],
        color=["Red"],
        cost=Cost(mana_cost={"Red": 1}),
        base_power=1,
        base_toughness=1,
        etb_ability=abilities.VoldarenEpicure,
    ),

   "Lightning_Bolt": Instant(
        name="Lightbing Bolt",
        ability=abilities.Bolt,
        color=["Red"],
        cost=Cost(mana_cost={"Red": 1}),
    ),

    "Kessig_Flamebreather": Creature(
        name="Kessig Flamebreather",
        subtype=["Human", "Shaman"],
        color=["Red"],
        cost=Cost(mana_cost={"Red": 1, "None": 1}),
        base_power=1,
        base_toughness=3,
        triggered_ability=abilities.KessigFlamebreather,
    ),

    "Guttersnipe": Creature(
        name="Guttersnipe",
        subtype=["Goblin", "Shaman"],
        color=["Red"],
        cost=Cost(mana_cost={"Red": 1, "None": 2}),
        base_power=2,
        base_toughness=2,
        triggered_ability=abilities.Guttersnipe,
    ),

}

for key, card in _ALL_CARDS.items():
    if isinstance(card, Creature):
        card.modifiers = []
