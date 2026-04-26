from __future__ import annotations


CLASS_RESOURCE_ORDER = ("grit", "ward", "edge", "satchel", "toxin", "focus")
CLASS_RESOURCE_LABELS = {
    "grit": "Grit",
    "ward": "Ward",
    "edge": "Edge",
    "satchel": "Satchel",
    "toxin": "Toxin",
    "focus": "Focus",
}
CLASS_RESOURCE_COLORS = {
    "grit": "yellow",
    "ward": "blue",
    "edge": "green",
    "satchel": "light_aqua",
    "toxin": "green",
    "focus": "magenta",
}
CLASS_RESOURCE_FEATURES = {
    "grit": ("warrior_grit",),
    "ward": ("mage_ward", "spellguard_ward"),
    "edge": ("rogue_edge",),
    "satchel": ("rogue_satchel",),
    "toxin": ("rogue_poison",),
    "focus": ("mage_focus",),
}
TEMPORARY_CLASS_RESOURCES = {"grit", "ward", "edge", "toxin", "focus"}
CLASS_MARK_FLAG_PREFIXES = ("class_mark", "rogue_mark", "rogue_poison")


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
    if resource == "ward":
        return max(4, 8 + actor.level + actor_casting_modifier(actor))
    if resource == "edge":
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
    for resource in TEMPORARY_CLASS_RESOURCES:
        if resource in getattr(actor, "resources", {}):
            actor.resources[resource] = 0
    for key in list(getattr(actor, "bond_flags", {})):
        if key.startswith(CLASS_MARK_FLAG_PREFIXES) or key.startswith("class_reaction"):
            actor.bond_flags.pop(key, None)
