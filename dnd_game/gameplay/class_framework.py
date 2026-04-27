from __future__ import annotations


CLASS_RESOURCE_ORDER = ("grit", "momentum", "combo", "fury", "blood_debt", "ward", "flow", "arc", "attunement", "edge", "shadow", "satchel", "toxin", "focus")
CLASS_RESOURCE_LABELS = {
    "grit": "Grit",
    "momentum": "Momentum",
    "combo": "Combo",
    "fury": "Fury",
    "blood_debt": "Blood Debt",
    "ward": "Ward",
    "flow": "Flow",
    "arc": "Arc",
    "attunement": "Attunement",
    "edge": "Edge",
    "shadow": "Shadow",
    "satchel": "Satchel",
    "toxin": "Toxin",
    "focus": "Focus",
}
CLASS_RESOURCE_COLORS = {
    "grit": "yellow",
    "momentum": "light_yellow",
    "combo": "light_green",
    "fury": "red",
    "blood_debt": "bright_red",
    "ward": "blue",
    "flow": "light_cyan",
    "arc": "light_magenta",
    "attunement": "cyan",
    "edge": "green",
    "shadow": "bright_black",
    "satchel": "light_aqua",
    "toxin": "green",
    "focus": "magenta",
}
CLASS_RESOURCE_FEATURES = {
    "grit": ("warrior_grit",),
    "momentum": ("juggernaut_momentum",),
    "combo": ("weapon_master_combo", "style_wheel"),
    "fury": ("berserker_fury",),
    "blood_debt": ("bloodreaver_blood_debt", "red_mark"),
    "ward": ("mage_ward", "spellguard_ward"),
    "flow": ("aethermancer_flow", "field_mend", "pulse_restore", "overflow_shell"),
    "arc": ("arcanist_arc", "pattern_charge", "detonate_pattern"),
    "attunement": ("elementalist_attunement", "elemental_weave", "ember_lance", "frost_shard", "volt_grasp"),
    "edge": ("rogue_edge",),
    "shadow": ("shadowguard_shadow", "false_target"),
    "satchel": ("rogue_satchel",),
    "toxin": ("rogue_poison", "poisoner_toxin", "black_drop"),
    "focus": ("mage_focus",),
}
TEMPORARY_CLASS_RESOURCES = {"grit", "momentum", "combo", "fury", "blood_debt", "ward", "flow", "arc", "attunement", "edge", "shadow", "toxin", "focus"}
CLASS_MARK_FLAG_PREFIXES = ("class_mark", "mage", "aethermancer", "arcanist", "elementalist", "rogue_mark", "rogue_poison", "shadowguard", "assassin", "alchemist", "warrior_fixated", "weapon_master", "berserker", "bloodreaver")


def actor_casting_modifier(actor) -> int:
    ability = getattr(actor, "spellcasting_ability", None)
    if ability:
        return actor.ability_mod(ability)
    return max(actor.ability_mod("INT"), actor.ability_mod("WIS"), actor.ability_mod("CHA"))


def actor_uses_class_resource(actor, resource: str) -> bool:
    if resource in getattr(actor, "max_resources", {}):
        return True
    features = set(getattr(actor, "features", []))
    return any(feature in features for feature in CLASS_RESOURCE_FEATURES.get(resource, ()))


def class_resource_cap(actor, resource: str) -> int:
    if resource == "grit":
        return max(2, 2 + actor.proficiency_bonus + actor.ability_mod("CON"))
    if resource == "momentum":
        return 6
    if resource == "combo":
        return 5
    if resource == "fury":
        return 6
    if resource == "blood_debt":
        return 5
    if resource == "ward":
        borrowed_capacity = 0
        if getattr(actor, "bond_flags", {}).get("mage_temporary_ward_capacity"):
            borrowed_capacity = int(getattr(actor, "max_resources", {}).get("ward", 0))
        return max(borrowed_capacity, 4, 8 + actor.level + actor_casting_modifier(actor))
    if resource == "flow":
        return 5
    if resource == "arc":
        return 6
    if resource == "attunement":
        return 4
    if resource == "edge":
        return 5
    if resource == "shadow":
        return 5
    if resource == "satchel":
        return max(1, 2 + actor.proficiency_bonus + actor.ability_mod("INT"))
    if resource == "toxin":
        return 5
    if resource == "focus":
        return 5
    return max(0, int(getattr(actor, "max_resources", {}).get(resource, 0)))


def class_resource_encounter_start(actor, resource: str) -> int:
    if resource == "grit":
        return 1
    if resource == "edge":
        return 0 if getattr(actor, "conditions", {}).get("surprised", 0) else 1
    if resource == "satchel":
        return class_resource_cap(actor, resource)
    if resource == "toxin":
        features = set(getattr(actor, "features", []))
        poisoner_features = {"poisoner_toxin", "black_drop", "green_needle", "bitter_cloud", "rot_thread", "bloom_in_the_blood"}
        if features & poisoner_features:
            return class_resource_cap(actor, resource)
    return 0


def synchronize_class_resources(actor, *, refill: bool = False, encounter_start: bool = False) -> None:
    for resource in CLASS_RESOURCE_ORDER:
        if not actor_uses_class_resource(actor, resource):
            continue
        cap = class_resource_cap(actor, resource)
        if cap <= 0:
            actor.max_resources.pop(resource, None)
            actor.resources.pop(resource, None)
            continue
        actor.max_resources[resource] = cap
        current = max(0, int(actor.resources.get(resource, class_resource_encounter_start(actor, resource))))
        if encounter_start:
            actor.resources[resource] = min(cap, class_resource_encounter_start(actor, resource))
        elif refill and resource == "satchel":
            actor.resources[resource] = cap
        else:
            actor.resources[resource] = min(current, cap)


def clear_class_combat_state(actor) -> None:
    borrowed_ward = bool(getattr(actor, "bond_flags", {}).get("mage_temporary_ward_capacity"))
    for resource in TEMPORARY_CLASS_RESOURCES:
        if resource in getattr(actor, "resources", {}):
            actor.resources[resource] = 0
    if borrowed_ward:
        actor.resources.pop("ward", None)
        actor.max_resources.pop("ward", None)
    for key in list(getattr(actor, "bond_flags", {})):
        if key.startswith(CLASS_MARK_FLAG_PREFIXES) or key.startswith("class_reaction"):
            actor.bond_flags.pop(key, None)
