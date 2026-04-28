from __future__ import annotations

from math import ceil

MAGIC_POINT_RESOURCE = "mp"
SPELL_SLOT_RESTORE_MP = 4

FULL_CASTER_CLASSES = {"Mage"}

FEATURE_CASTER_IDS = {"magic_initiate", "racial_magic"}

SPELL_MP_COSTS: dict[str, int] = {
    "arcane_bolt": 1,
    "minor_channel": 1,
    "arc_pulse": 1,
    "marked_angle": 1,
    "ember_lance": 1,
    "frost_shard": 1,
    "volt_grasp": 1,
    "burning_line": 4,
    "lockfrost": 4,
    "field_mend": 3,
    "pulse_restore": 4,
    "triage_line": 3,
    "clean_breath": 2,
    "anchor_shell": 3,
    "ward_shell": 2,
    "blue_glass_palm": 1,
    "lockstep_field": 3,
}


def arcane_bolt_mp_cost(actor=None) -> int:
    level = max(1, int(getattr(actor, "level", 1) if actor is not None else 1))
    return min(4, 1 + (level - 1) // 3)


def magic_point_cost(spell_id: str, actor=None) -> int:
    if spell_id == "arcane_bolt":
        return arcane_bolt_mp_cost(actor)
    return SPELL_MP_COSTS[spell_id]


def spellcasting_modifier(actor) -> int:
    ability = getattr(actor, "spellcasting_ability", None)
    if ability is None:
        return 0
    return max(0, actor.ability_mod(ability))


def has_feature_caster_access(actor) -> bool:
    features = set(getattr(actor, "features", []))
    return any(feature in features for feature in FEATURE_CASTER_IDS)


def max_magic_points(actor) -> int:
    spell_mod = spellcasting_modifier(actor)
    level = max(1, int(getattr(actor, "level", 1)))
    class_name = getattr(actor, "class_name", "")
    if class_name in FULL_CASTER_CLASSES:
        return 6 + (4 * level) + spell_mod
    if has_feature_caster_access(actor):
        return 3 + spell_mod
    return 0


def synchronize_magic_points(actor, *, refill: bool) -> int:
    maximum = max_magic_points(actor)
    if maximum <= 0:
        actor.max_resources.pop(MAGIC_POINT_RESOURCE, None)
        actor.resources.pop(MAGIC_POINT_RESOURCE, None)
        return 0
    actor.max_resources[MAGIC_POINT_RESOURCE] = maximum
    current = int(actor.resources.get(MAGIC_POINT_RESOURCE, maximum))
    actor.resources[MAGIC_POINT_RESOURCE] = maximum if refill else min(current, maximum)
    return maximum


def current_magic_points(actor) -> int:
    return int(actor.resources.get(MAGIC_POINT_RESOURCE, 0))


def maximum_magic_points(actor) -> int:
    return int(actor.max_resources.get(MAGIC_POINT_RESOURCE, 0))


def has_magic_points(actor, cost: int) -> bool:
    return current_magic_points(actor) >= max(0, cost)


def spend_magic_points(actor, cost: int) -> bool:
    cost = max(0, cost)
    if not has_magic_points(actor, cost):
        return False
    actor.resources[MAGIC_POINT_RESOURCE] = current_magic_points(actor) - cost
    return True


def restore_magic_points(actor, amount: int) -> int:
    maximum = maximum_magic_points(actor)
    if maximum <= 0:
        return 0
    current = current_magic_points(actor)
    restored = min(maximum - current, max(0, amount))
    if restored <= 0:
        return 0
    actor.resources[MAGIC_POINT_RESOURCE] = current + restored
    return restored


def restore_all_magic_points(actor) -> int:
    maximum = maximum_magic_points(actor)
    if maximum <= 0:
        return 0
    current = current_magic_points(actor)
    actor.resources[MAGIC_POINT_RESOURCE] = maximum
    return max(0, maximum - current)


def restore_half_magic_points(actor) -> int:
    maximum = maximum_magic_points(actor)
    if maximum <= 0:
        return 0
    return restore_magic_points(actor, ceil(maximum / 2))


def magic_point_summary(actor) -> str:
    maximum = maximum_magic_points(actor)
    if maximum <= 0:
        return "None"
    return f"{current_magic_points(actor)}/{maximum}"


def spell_slot_restore_units_to_mp(units: int) -> int:
    return max(0, units) * SPELL_SLOT_RESTORE_MP
