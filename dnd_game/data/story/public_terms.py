from __future__ import annotations

import re
from collections.abc import Mapping


CLASS_PUBLIC_LABELS: dict[str, str] = {}


RACE_PUBLIC_LABELS = {
    "Human": "Human",
    "Dwarf": "Dwarf",
    "Elf": "Elf",
    "Halfling": "Halfling",
    "Dragonborn": "Forged",
    "Gnome": "Unrecorded",
    "Half-Elf": "Astral Elf",
    "Half-Orc": "Orc-Blooded",
    "Tiefling": "Fire-Blooded",
    "Goliath": "Riverfolk",
    "Orc": "Orc",
}


ABILITY_PUBLIC_LABELS = {
    "STR": "Strength",
    "DEX": "Agility",
    "CON": "Endurance",
    "INT": "Intelligence",
    "WIS": "Wisdom",
    "CHA": "Charisma",
}


ABILITY_FULL_LABELS = {
    "STR": "Strength",
    "DEX": "Dexterity",
    "CON": "Constitution",
    "INT": "Intelligence",
    "WIS": "Wisdom",
    "CHA": "Charisma",
}


SKILL_PUBLIC_LABELS: dict[str, str] = {}


SPELL_PUBLIC_LABELS = {
    "arcane_bolt": "Arcane Bolt",
    "minor_channel": "Minor Channel",
    "arc_pulse": "Arc Pulse",
    "marked_angle": "Marked Angle",
    "ember_lance": "Ember Lance",
    "frost_shard": "Frost Shard",
    "volt_grasp": "Volt Grasp",
    "burning_line": "Burning Line",
    "lockfrost": "Lockfrost",
    "field_mend": "Field Mend",
    "pulse_restore": "Pulse Restore",
    "triage_line": "Triage Line",
    "clean_breath": "Clean Breath",
    "anchor_shell": "Anchor Shell",
    "ward_shell": "Ward Shell",
    "blue_glass_palm": "Blue Glass Palm",
    "lockstep_field": "Lockstep Field",
}


SPELL_NAME_TO_ID = {
    "Arcane Bolt": "arcane_bolt",
    "Arc Pulse": "arc_pulse",
    "Marked Angle": "marked_angle",
    "Ember Lance": "ember_lance",
    "Frost Shard": "frost_shard",
    "Volt Grasp": "volt_grasp",
    "Burning Line": "burning_line",
    "Lockfrost": "lockfrost",
    "Field Mend": "field_mend",
    "Pulse Restore": "pulse_restore",
    "Triage Line": "triage_line",
    "Clean Breath": "clean_breath",
    "Anchor Shell": "anchor_shell",
    "Ward Shell": "ward_shell",
    "Blue Glass Palm": "blue_glass_palm",
    "Lockstep Field": "lockstep_field",
}


FEATURE_PUBLIC_LABELS = {
    "sneak_attack": "Veilstrike",
    "expertise": "Deep Practice",
    "mage_charge": "Charge",
    "mage_focus": "Focus",
    "arcane_bolt": "Arcane Bolt",
    "minor_channel": "Minor Channel",
    "pattern_read": "Pattern Read",
    "ground": "Ground",
    "focused_eye": "Focused Eye",
    "field_sense": "Field Sense",
    "steady_hands": "Steady Hands",
    "counter_cadence": "Counter-Cadence",
    "darkvision": "Lowlight Sight",
    "dwarven_resilience": "Dwarven Resilience",
    "keen_senses": "Keen Senses",
    "fey_ancestry": "Signal Distance",
    "lucky": "Halfling Luck",
    "brave": "Small Courage",
    "draconic_presence": "Forged Presence",
    "gnome_cunning": "Unrecorded Cunning",
    "relentless_endurance": "Orcish Grit",
    "menacing": "Hard Stare",
    "hellish_resistance": "Fire-Blooded Resistance",
    "stone_endurance": "Riverfolk Endurance",
    "adrenaline_rush": "Orc Rush",
    "cunning_action": "Veil Step",
    "rogue_edge": "Edge",
    "rogue_mark": "Mark Work",
    "rogue_satchel": "Satchel Kit",
    "rogue_poison": "Poison Work",
    "tool_read": "Tool Read",
    "rogue_skirmish": "Skirmish",
    "slip_away": "Slip Away",
    "rogue_feint": "Feint",
    "dirty_trick": "Dirty Trick",
    "shadowguard_shadow": "Shadow",
    "false_target": "False Target",
    "smoke_pin": "Smoke Pin",
    "cover_the_healer": "Cover The Healer",
    "death_mark": "Death Mark",
    "quiet_knife": "Quiet Knife",
    "between_plates": "Between Plates",
    "sudden_end": "Sudden End",
    "poisoner_toxin": "Toxin Prep",
    "black_drop": "Black Drop",
    "green_needle": "Green Needle",
    "bitter_cloud": "Bitter Cloud",
    "rot_thread": "Rot Thread",
    "bloom_in_the_blood": "Bloom In The Blood",
    "alchemist_quick_mix": "Quick Mix",
    "redcap_tonic": "Redcap Tonic",
    "smoke_jar": "Smoke Jar",
    "bitter_acid": "Bitter Acid",
    "field_stitch": "Field Stitch",
    "improved_sneak_attack": "Deadly Veilstrike",
    "evasion": "Evasion",
    "arcane_focus": "Channel Focus",
    "warrior_grit": "Grit",
    "warrior_guard": "Guard Stance",
    "warrior_shove": "Shove",
    "warrior_pin": "Pin",
    "warrior_rally": "Warrior Rally",
    "weapon_read": "Weapon Read",
    "juggernaut_momentum": "Momentum",
    "iron_draw": "Iron Draw",
    "shoulder_in": "Shoulder In",
    "weapon_master_combo": "Combo",
    "style_wheel": "Style Wheel",
    "measure_twice": "Measure Twice",
    "clean_line": "Clean Line",
    "dent_the_shell": "Dent The Shell",
    "hook_the_guard": "Hook The Guard",
    "berserker_fury": "Fury",
    "redline": "Redline",
    "reckless_cut": "Reckless Cut",
    "teeth_set": "Teeth Set",
    "drink_the_hurt": "Drink The Hurt",
    "bloodreaver_blood_debt": "Blood Debt",
    "red_mark": "Red Mark",
    "blood_price": "Blood Price",
    "war_salve_strike": "War-Salve Strike",
    "open_the_ledger": "Open The Ledger",
    "mage_ward": "Ward",
    "arcanist_arc": "Arc",
    "pattern_charge": "Pattern Charge",
    "arc_pulse": "Arc Pulse",
    "marked_angle": "Marked Angle",
    "quiet_sum": "Quiet Sum",
    "detonate_pattern": "Detonate Pattern",
    "elementalist_attunement": "Attunement",
    "elemental_weave": "Elemental Weave",
    "ember_lance": "Ember Lance",
    "frost_shard": "Frost Shard",
    "volt_grasp": "Volt Grasp",
    "change_weather_hand": "Change Weather In The Hand",
    "burning_line": "Burning Line",
    "lockfrost": "Lockfrost",
    "aethermancer_flow": "Flow",
    "field_mend": "Field Mend",
    "pulse_restore": "Pulse Restore",
    "triage_line": "Triage Line",
    "clean_breath": "Clean Breath",
    "steady_pulse": "Steady Pulse",
    "overflow_shell": "Overflow Shell",
    "spellguard_ward": "Spellguard Ward",
    "anchor_shell": "Anchor Shell",
    "ward_shell": "Ward Shell",
    "blue_glass_palm": "Blue Glass Palm",
    "lockstep_field": "Lockstep Field",
    "hard_lesson": "Hard Lesson",
    "line_holder": "Line Holder",
    "weapon_familiarity": "Weapon Familiarity",
}


RESOURCE_PUBLIC_LABELS = {
    "mp": "MP",
    "grit": "grit",
    "momentum": "momentum",
    "combo": "combo",
    "fury": "fury",
    "blood_debt": "blood debt",
    "ward": "ward",
    "flow": "flow",
    "arc": "arc",
    "attunement": "attunement",
    "edge": "edge",
    "shadow": "shadow",
    "satchel": "satchel",
    "toxin": "toxin",
    "focus": "focus",
}


TERM_REPLACEMENTS = (
    (r"\bArmor Class\b", "Defense"),
    (r"\barmor class\b", "Defense"),
    (r"\bSaving Throws\b", "Resist Checks"),
    (r"\bsaving throws\b", "resist checks"),
    (r"\bSaving Throw\b", "Resist Check"),
    (r"\bsaving throw\b", "resist check"),
    (r"\bspell attack rolls\b", "channel strike checks"),
    (r"\bspell attack roll\b", "channel strike check"),
    (r"\bspell attack\b", "channel strike"),
    (r"\bSpell attack\b", "Channel strike"),
    (r"\bAttack Rolls\b", "Strike Checks"),
    (r"\battack rolls\b", "strike checks"),
    (r"\bAttack Roll\b", "Strike Check"),
    (r"\battack roll\b", "strike check"),
    (r"\bweapon attacks\b", "weapon strikes"),
    (r"\bWeapon attacks\b", "Weapon strikes"),
    (r"\bspell slots\b", "charge bands"),
    (r"\bSpell Slots\b", "Charge Bands"),
    (r"\bspell slot\b", "charge band"),
    (r"\bSpell Slot\b", "Charge Band"),
    (r"\bspellcasting\b", "channeling"),
    (r"\bSpellcasting\b", "Channeling"),
    (r"\bspell damage\b", "channel damage"),
    (r"\bSpell damage\b", "Channel damage"),
    (r"\bcantrips\b", "minor channels"),
    (r"\bCantrips\b", "Minor channels"),
    (r"\bcantrip\b", "minor channel"),
    (r"\bCantrip\b", "Minor channel"),
    (r"\bmagic item\b", "relic"),
    (r"\bMagic item\b", "Relic"),
    (r"\bmagic items\b", "relics"),
    (r"\bMagic items\b", "Relics"),
    (r"\bscroll\b", "script"),
    (r"\bScroll\b", "Script"),
    (r"\badvantage\b", "edge"),
    (r"\bAdvantage\b", "Edge"),
    (r"\bdisadvantage\b", "strain"),
    (r"\bDisadvantage\b", "Strain"),
)


def class_label(class_name: str) -> str:
    return CLASS_PUBLIC_LABELS.get(class_name, class_name)


def race_label(race_name: str) -> str:
    return RACE_PUBLIC_LABELS.get(race_name, race_name)


def ability_label(code: str, *, include_code: bool = False) -> str:
    public = ABILITY_PUBLIC_LABELS.get(code, code)
    if include_code and code in ABILITY_PUBLIC_LABELS:
        return f"{public} ({code})"
    return public


def ability_full_label(code: str) -> str:
    public = ABILITY_PUBLIC_LABELS.get(code)
    base = ABILITY_FULL_LABELS.get(code, code)
    return f"{public} ({base})" if public and public != base else base


def skill_label(skill_name: str) -> str:
    return SKILL_PUBLIC_LABELS.get(skill_name, skill_name)


def skill_option_label(skill_name: str) -> str:
    public = skill_label(skill_name)
    return public if public == skill_name else f"{public} ({skill_name})"


def feature_label(feature_id: str) -> str:
    if feature_id in FEATURE_PUBLIC_LABELS:
        return FEATURE_PUBLIC_LABELS[feature_id]
    return feature_id.replace("_", " ").title()


def resource_label(resource_name: str) -> str:
    if resource_name.startswith("spell_slots_"):
        return f"charge band {resource_name.rsplit('_', 1)[-1]}"
    return RESOURCE_PUBLIC_LABELS.get(resource_name, resource_name.replace("_", " "))


def spell_label(spell_id_or_name: str, fallback: str | None = None) -> str:
    spell_id = SPELL_NAME_TO_ID.get(spell_id_or_name, spell_id_or_name)
    return SPELL_PUBLIC_LABELS.get(spell_id, fallback or spell_id_or_name.replace("_", " ").title())


def class_option_label(class_name: str) -> str:
    public = class_label(class_name)
    return public if public == class_name else f"{public} ({class_name})"


def race_option_label(race_name: str) -> str:
    public = race_label(race_name)
    return public if public == race_name else f"{public} ({race_name})"


def character_role_line(race_name: str, class_name: str) -> str:
    return f"{race_label(race_name)} {class_label(class_name)}"


def format_bonus_list(bonuses: Mapping[str, int], *, include_codes: bool = False) -> str:
    return ", ".join(f"{ability_label(ability, include_code=include_codes)} +{value}" for ability, value in bonuses.items())


def marks_label(value: int) -> str:
    return f"{value} gold"


def guard_label(value: int) -> str:
    return f"Guard {value}"


def target_guard_label(value: int) -> str:
    return f"Guard {value}"


def d20_edge_label(advantage_state: int) -> str:
    if advantage_state > 0:
        return "edge"
    if advantage_state < 0:
        return "strain"
    return ""


def rules_text(text: str) -> str:
    rendered = text
    for pattern, replacement in TERM_REPLACEMENTS:
        rendered = re.sub(pattern, replacement, rendered)
    return rendered
