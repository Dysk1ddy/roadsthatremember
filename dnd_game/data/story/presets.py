from __future__ import annotations

from .factories import build_character


PRESET_CHARACTERS: dict[str, dict[str, object]] = {
    "Warrior": {
        "name": "Mara Gatehand",
        "race": "Human",
        "background": "Soldier",
        "base_ability_scores": {"STR": 15, "DEX": 12, "CON": 14, "INT": 8, "WIS": 13, "CHA": 10},
        "class_skill_choices": ["Athletics", "Perception"],
        "description": "A shield-line route guard built for Grit, Guard Stance, shoves, and reading armored enemies.",
    },
    "Mage": {
        "name": "Sella Wardinglass",
        "race": "Gnome",
        "background": "Sage",
        "base_ability_scores": {"STR": 8, "DEX": 13, "CON": 14, "INT": 15, "WIS": 12, "CHA": 10},
        "class_skill_choices": ["Arcana", "Investigation", "Medicine"],
        "description": "A field channeler built for Pattern Read, Minor Channel, ward pressure, and ruin-side problem solving.",
    },
    "Rogue": {
        "name": "Tamsin Lockreed",
        "race": "Halfling",
        "background": "Criminal",
        "base_ability_scores": {"STR": 8, "DEX": 15, "CON": 13, "INT": 12, "WIS": 14, "CHA": 10},
        "class_skill_choices": ["Acrobatics", "Insight", "Perception", "Sleight of Hand"],
        "expertise_choices": ["Stealth", "Perception"],
        "description": "A quiet scout and lockbreaker tuned for Edge, Veilstrike, stealth, and reliable skill coverage.",
    },
}


def build_preset_character(class_name: str):
    preset = PRESET_CHARACTERS[class_name]
    character = build_character(
        name=str(preset["name"]),
        race=str(preset["race"]),
        class_name=class_name,
        background=str(preset["background"]),
        base_ability_scores=dict(preset["base_ability_scores"]),
        class_skill_choices=list(preset["class_skill_choices"]),
        expertise_choices=list(preset.get("expertise_choices", [])),
        notes=[str(preset["description"]), "Preset build: optimized for faster testing and quick starts."],
        inventory={"Healing Potion": 1},
    )
    return character
