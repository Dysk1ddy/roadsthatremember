from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass

from ..data.story.public_terms import ability_label, spell_label
from ..dice import D20Outcome, roll, roll_d20
from ..items import ITEMS
from ..ui.colors import rich_style_name, strip_ansi
from ..ui.rich_render import Group, Panel, box
from .class_framework import CLASS_RESOURCE_COLORS, CLASS_RESOURCE_LABELS, CLASS_RESOURCE_ORDER
from .class_framework import actor_uses_class_resource, class_resource_cap, clear_class_combat_state
from .class_framework import synchronize_class_resources
from .difficulty_policy import ACT_DIFFICULTY_BANDS, clamp_dc_to_band
from .magic_points import current_magic_points, magic_point_cost, spend_magic_points
from .status_effects import STANCE_STATUS_BY_KEY, STANCE_STATUS_NAMES


PHYSICAL_DEFENSE_DAMAGE_TYPES = {"", "slashing", "piercing", "bludgeoning"}
STANCE_LABELS = {
    "neutral": "Neutral",
    "guard": "Guard",
    "brace": "Brace",
    "mobile": "Mobile",
    "aggressive": "Aggressive",
    "aim": "Aim",
    "press": "Press",
}
STANCE_SUMMARIES = {
    "neutral": "No stance modifiers.",
    "guard": "+20% Defense, +1 Avoidance, +2 Stability, -2 Accuracy.",
    "brace": "+10% Defense, +4 Stability, -1 Avoidance, -1 Accuracy.",
    "mobile": "+2 Avoidance, +2 retreat checks, -5% Defense, -1 Stability.",
    "aggressive": "+2 Accuracy, +2 weapon damage, -10% Defense, -1 Avoidance.",
    "aim": "+2 Accuracy, -5% Defense, -2 Avoidance, -1 Stability.",
    "press": "+1 Accuracy, +10% Armor Break, +1 Stability, -5% Defense, -1 Avoidance.",
}
STANCE_ORDER = ("neutral", "guard", "brace", "mobile", "aggressive", "aim", "press")


@dataclass(slots=True)
class DamageResolution:
    raw_damage: int = 0
    resisted_damage: int = 0
    defense_percent: int = 0
    armor_break_percent: int = 0
    mitigated_damage: int = 0
    ward_absorbed: int = 0
    temp_hp_absorbed: int = 0
    hp_damage: int = 0
    glance: bool = False
    wound: bool = False


class CombatResolutionMixin:
    @contextmanager
    def temporary_roll_display_bonus(self, bonus: int):
        with self.temporary_roll_animation_metadata(display_bonus=bonus):
            yield

    def roll_with_display_bonus(
        self,
        expression: str,
        *,
        bonus: int = 0,
        critical: bool = False,
        style: str | None = None,
        context_label: str | None = None,
        outcome_kind: str | None = None,
    ):
        return self.roll_with_animation_context(
            expression,
            bonus=bonus,
            critical=critical,
            style=style,
            context_label=context_label,
            outcome_kind=outcome_kind,
        )

    def spend_mp_for_spell(self, caster, spell_id: str, spell_name: str) -> bool:
        cost = magic_point_cost(spell_id)
        if spend_magic_points(caster, cost):
            return True
        channel_name = spell_label(spell_id, spell_name)
        self.say(
            f"{self.style_name(caster)} needs {cost} MP to use {channel_name}, "
            f"but has {current_magic_points(caster)}."
        )
        return False

    def equipped_weapon_item(self, actor):
        return ITEMS.get(actor.equipment_slots.get("main_hand", "")) if getattr(actor, "equipment_slots", None) else None

    def equipped_off_hand_weapon_item(self, actor):
        if not getattr(actor, "equipment_slots", None):
            return None
        item = ITEMS.get(actor.equipment_slots.get("off_hand", ""))
        if item is None or item.weapon is None:
            return None
        return item

    def actor_is_dodging(self, actor) -> bool:
        return getattr(actor, "name", None) in getattr(self, "_active_dodging_names", frozenset())

    def dodge_applies_against_attacker(self, defender, attacker) -> bool:
        if not self.actor_is_dodging(defender):
            return False
        defender_features = set(getattr(defender, "features", []))
        if self.has_status(defender, "blinded") and "blind_sense" not in defender_features:
            return False
        if self.has_status(attacker, "invisible") and "blind_sense" not in defender_features:
            return False
        return True

    def trigger_blacklake_adjudicator_reflection(self, attacker, target, *, source: str) -> None:
        if getattr(target, "archetype", "") != "blacklake_adjudicator":
            return
        if getattr(attacker, "dead", False) or getattr(attacker, "current_hp", 0) <= 0:
            return
        current_round = int(getattr(self, "_active_round_number", 0) or 0)
        if current_round and int(target.bond_flags.get("mirror_verdict_round", -1)) == current_round:
            return
        target.bond_flags["mirror_verdict_round"] = current_round
        actual = self.apply_damage(
            attacker,
            self.roll_with_display_bonus(
                "1d6",
                style="damage",
                context_label=f"{target.name}'s mirror verdict",
                outcome_kind="damage",
            ).total,
            damage_type="force",
        )
        self.say(f"{target.name}'s mirror verdict throws {self.style_damage(actual)} force back into {attacker.name} from {source}.")
        self.announce_downed_target(attacker)

    def break_invisibility_from_hostile_action(self, actor) -> None:
        if self.has_status(actor, "invisible"):
            self.clear_status(actor, "invisible")
            self.say(f"{self.style_name(actor)} gives away their position by striking.")

    def weapon_attack_ability_for(self, actor, weapon) -> str:
        if weapon.ability == "SPELL":
            return actor.spellcasting_ability or "INT"
        if weapon.ability == "DEX":
            return "DEX"
        if weapon.ability == "FINESSE" or weapon.finesse:
            return "DEX" if actor.ability_mod("DEX") >= actor.ability_mod("STR") else "STR"
        return weapon.ability

    def weapon_attack_bonus_for(self, actor, weapon) -> int:
        return (
            actor.ability_mod(self.weapon_attack_ability_for(actor, weapon))
            + actor.proficiency_bonus
            + weapon.to_hit_bonus
            + actor.equipment_bonuses.get("attack", 0)
            + actor.gear_bonuses.get("attack", 0)
            + actor.relationship_bonuses.get("attack", 0)
        )

    def weapon_damage_bonus_for(self, actor, weapon, *, include_ability_mod: bool = True) -> int:
        ability_mod = actor.ability_mod(self.weapon_attack_ability_for(actor, weapon))
        if not include_ability_mod:
            ability_mod = min(0, ability_mod)
        return (
            ability_mod
            + weapon.damage_bonus
            + actor.equipment_bonuses.get("damage", 0)
            + actor.gear_bonuses.get("damage", 0)
            + actor.relationship_bonuses.get("damage", 0)
        )

    def status_accuracy_modifier(self, actor) -> int:
        return self.status_value(actor, "attack_bonus") - self.status_value(actor, "attack_penalty")

    def status_damage_modifier(self, actor) -> int:
        return self.status_value(actor, "damage_bonus")

    def current_difficulty_act(self) -> int:
        if self.state is None:
            return 1
        return 2 if int(getattr(self.state, "current_act", 1)) >= 2 else 1

    def current_act1_room_role(self) -> str | None:
        dungeon_getter = getattr(self, "current_act1_dungeon", None)
        room_getter = getattr(self, "current_act1_room", None)
        if not callable(dungeon_getter) or not callable(room_getter):
            return None
        try:
            dungeon = dungeon_getter()
            if dungeon is None:
                return None
            room = room_getter(dungeon)
        except Exception:
            return None
        role = str(getattr(room, "role", "")).strip().lower()
        return role or None

    def is_recruitment_check(self, context: str) -> bool:
        lowered = context.lower()
        companion_markers = ("bryn", "nim", "irielle", "kaelis", "rhogar", "tolan")
        return "convince" in lowered and any(marker in lowered for marker in companion_markers)

    def in_boss_difficulty_scene(self) -> bool:
        if self.state is None:
            return False
        room_role = self.current_act1_room_role()
        if room_role == "boss":
            return True
        return self.state.current_scene in {"forge_of_spells"}

    def in_hostile_skill_scene(self) -> bool:
        if self.state is None:
            return False
        room_role = self.current_act1_room_role()
        if room_role is not None:
            return room_role in {"entrance", "combat", "event", "treasure", "boss"}
        return self.state.current_scene in {
            "background_prologue",
            "road_ambush",
            "neverwinter_wood_survey_camp",
            "stonehollow_dig",
            "act2_midpoint_convergence",
            "broken_prospect",
            "south_adit",
            "wave_echo_outer_galleries",
            "black_lake_causeway",
            "forge_of_spells",
        }

    def skill_check_category(self, context: str) -> str:
        if self.is_recruitment_check(context):
            return "recruitment"
        if self.in_boss_difficulty_scene():
            return "boss"
        if getattr(self, "_in_combat", False):
            return "combat"
        if getattr(self, "_random_encounter_active", False):
            return "random"
        if self.in_hostile_skill_scene():
            return "combat"
        return "regular"

    def effective_skill_dc(self, dc: int, *, context: str) -> int:
        if self.state is None:
            return dc
        act = self.current_difficulty_act()
        category = self.skill_check_category(context)
        minimum_tier, maximum_tier = ACT_DIFFICULTY_BANDS[act][category]
        return clamp_dc_to_band(dc, minimum_tier, maximum_tier)

    def ally_pressure_bonus(self, attacker, allies, *, ranged: bool) -> int:
        if not any(ally.is_conscious() and ally is not attacker for ally in allies):
            return 0
        # A light flanking-style bonus keeps fights dynamic without granting
        # near-constant full edge.
        return 1 if ranged else 2

    def has_damage_resistance(self, actor, damage_type: str) -> bool:
        if not damage_type:
            return False
        if actor.gear_bonuses.get(f"resist_{damage_type}", 0):
            return True
        return self.has_status(actor, f"resist_{damage_type}")

    def damage_type_uses_defense(self, damage_type: str) -> bool:
        return (damage_type or "").lower() in PHYSICAL_DEFENSE_DAMAGE_TYPES

    def armor_defense_percent(self, armor) -> int:
        if armor is None:
            return 0
        explicit = getattr(armor, "defense_percent", None)
        if explicit is not None:
            return max(0, int(explicit))
        armor_type = str(getattr(armor, "armor_type", "") or "").lower()
        base_ac = int(getattr(armor, "base_ac", 10))
        if armor_type == "clothing":
            return max(0, (base_ac - 10) * 5)
        if getattr(armor, "heavy", False) or armor_type == "heavy":
            return min(45, 35 + max(0, base_ac - 16) * 10)
        if armor_type == "medium":
            return 20 if base_ac <= 13 else min(35, 25 + max(0, base_ac - 14) * 5)
        if armor_type == "light":
            return min(25, 10 + max(0, base_ac - 11) * 5)
        return min(70, max(0, (base_ac - 10) * 5))

    def defense_bonus_percent(self, actor) -> int:
        total = 0
        for bonuses in (actor.equipment_bonuses, actor.gear_bonuses, actor.relationship_bonuses):
            total += int(bonuses.get("defense_percent", 0))
            total += int(bonuses.get("defense", 0)) * 5
            total += int(bonuses.get("AC", 0)) * 5
        if self.has_status(actor, "raised_shield") and getattr(actor, "shield", False):
            total += self.raised_shield_defense_percent(actor)
        total += self.status_value(actor, "defense_bonus_percent")
        return total

    def defense_cap_percent(self, actor) -> int:
        bonus_cap = 0
        for bonuses in (actor.equipment_bonuses, actor.gear_bonuses, actor.relationship_bonuses):
            cap = int(bonuses.get("defense_cap_percent", bonuses.get("defense_cap", 0)))
            if cap > 0:
                bonus_cap = max(bonus_cap, cap)
        armor = getattr(actor, "armor", None)
        armor_cap = int(getattr(armor, "defense_cap_percent", 0) or 0)
        armor_type = str(getattr(armor, "armor_type", "") or "").lower() if armor is not None else ""
        if armor_cap <= 0:
            if armor is None or (armor_type in {"clothing", "light"} and not getattr(armor, "heavy", False)):
                armor_cap = 45
            else:
                armor_cap = 75
        if "heavy_armor_specialist" in getattr(actor, "features", []):
            armor_cap = max(armor_cap, 80)
        return bonus_cap or armor_cap

    def shield_defense_percent(self, actor) -> int:
        if not getattr(actor, "shield", False):
            return 0
        total = 0
        for bonuses in (actor.equipment_bonuses, actor.gear_bonuses, actor.relationship_bonuses):
            total += int(bonuses.get("shield_defense_percent", 0))
            total += int(bonuses.get("shield_defense", 0)) * 5
        return total if total > 0 else 5

    def raised_shield_defense_percent(self, actor) -> int:
        total = 0
        for bonuses in (actor.equipment_bonuses, actor.gear_bonuses, actor.relationship_bonuses):
            total += int(bonuses.get("raised_shield_defense_percent", 0))
            total += int(bonuses.get("raised_shield_defense", 0)) * 5
        return total if total > 0 else 10

    def total_armor_break_percent(self, target, *, source_actor=None, incoming_percent: int = 0, incoming_steps: int = 0) -> int:
        total = max(0, int(incoming_percent)) + max(0, int(incoming_steps)) * 10
        total += max(0, int(getattr(target, "conditions", {}).get("armor_broken", 0))) * 10
        total += self.status_value(target, "armor_break_percent")
        if source_actor is not None:
            for bonuses in (source_actor.equipment_bonuses, source_actor.gear_bonuses, source_actor.relationship_bonuses):
                total += int(bonuses.get("armor_break_percent", 0))
                total += int(bonuses.get("armor_break", 0)) * 10
            total += self.status_value(source_actor, "outgoing_armor_break_percent")
            total += self.status_value(source_actor, "armor_break_percent")
            total += self.status_value(source_actor, "armor_break") * 10
        return max(0, total)

    def effective_defense_percent(
        self,
        actor,
        *,
        damage_type: str = "",
        armor_break_percent: int = 0,
    ) -> int:
        if not self.damage_type_uses_defense(damage_type):
            return 0
        defense = self.armor_defense_percent(getattr(actor, "armor", None))
        defense += self.shield_defense_percent(actor)
        defense += self.defense_bonus_percent(actor)
        defense -= max(0, int(armor_break_percent))
        return max(0, min(defense, self.defense_cap_percent(actor)))

    def effective_avoidance(self, actor) -> int:
        if any(self.has_status(actor, status) for status in ("stunned", "paralyzed", "unconscious")):
            return -5
        dex_mod = actor.ability_mod("DEX")
        armor = getattr(actor, "armor", None)
        if armor is not None:
            cap = 0 if getattr(armor, "heavy", False) else getattr(armor, "dex_cap", None)
            if cap is not None:
                dex_mod = min(dex_mod, int(cap))
        total = dex_mod
        for bonuses in (actor.equipment_bonuses, actor.gear_bonuses, actor.relationship_bonuses):
            total += int(bonuses.get("avoidance", 0))
            total += int(bonuses.get("avoidance_bonus", 0))
        total += self.status_value(actor, "avoidance_bonus")
        total -= self.status_value(actor, "avoidance_penalty")
        return total

    def effective_attack_target_number(self, actor) -> int:
        return max(1, 10 + self.effective_avoidance(actor))

    def attack_target_label(self, target_number: int) -> str:
        return f"Avoidance {target_number}"

    def last_damage_resolution(self) -> DamageResolution:
        return getattr(self, "_last_damage_resolution", DamageResolution())

    def last_damage_was_glance(self) -> bool:
        return self.last_damage_resolution().glance

    def last_damage_caused_wound(self) -> bool:
        return self.last_damage_resolution().wound

    def actor_uses_class_resource(self, actor, resource: str) -> bool:
        return actor_uses_class_resource(actor, resource)

    def class_resource_label(self, resource: str) -> str:
        return CLASS_RESOURCE_LABELS.get(resource, resource.replace("_", " ").title())

    def class_resource_max(self, actor, resource: str) -> int:
        return class_resource_cap(actor, resource)

    def synchronize_class_resources(self, actor, *, refill: bool = False, encounter_start: bool = False) -> None:
        synchronize_class_resources(actor, refill=refill, encounter_start=encounter_start)

    def prepare_class_resources_for_combat(self, actor) -> None:
        self.synchronize_class_resources(actor, encounter_start=True)

    def grant_class_resource(self, actor, resource: str, amount: int = 1, *, source: str = "") -> int:
        if amount <= 0 or not self.actor_uses_class_resource(actor, resource):
            return 0
        if resource in {"grit", "edge", "toxin", "focus"} and not getattr(self, "_in_combat", False):
            return 0
        maximum = self.class_resource_max(actor, resource)
        if maximum <= 0:
            return 0
        actor.max_resources[resource] = maximum
        previous = max(0, int(actor.resources.get(resource, 0)))
        actor.resources[resource] = min(maximum, previous + amount)
        gained = actor.resources[resource] - previous
        if gained > 0:
            label = self.class_resource_label(resource)
            source_text = f" from {source}" if source else ""
            self.say(f"{self.style_name(actor)} gains {gained} {label}{source_text}.")
        return gained

    def spend_class_resource(self, actor, resource: str, amount: int = 1) -> bool:
        if amount <= 0:
            return True
        if not self.actor_uses_class_resource(actor, resource):
            return False
        self.synchronize_class_resources(actor)
        current = max(0, int(actor.resources.get(resource, 0)))
        if current < amount:
            return False
        actor.resources[resource] = current - amount
        return True

    def grant_ward(self, actor, amount: int, *, source: str = "") -> int:
        return self.grant_class_resource(actor, "ward", amount, source=source)

    def absorb_ward_damage(self, actor, amount: int, *, source_actor=None, damage_type: str = "") -> int:
        if amount <= 0 or not self.actor_uses_class_resource(actor, "ward"):
            return 0
        current = max(0, int(actor.resources.get("ward", 0)))
        if current <= 0:
            return 0
        absorbed = min(current, amount)
        actor.resources["ward"] = current - absorbed
        if absorbed > 0:
            self.on_ward_absorbed(actor, source_actor, absorbed=absorbed, damage_type=damage_type)
        return absorbed

    def on_ward_absorbed(self, actor, source_actor, *, absorbed: int, damage_type: str) -> None:
        if absorbed <= 0:
            return
        actor.bond_flags["last_ward_absorbed"] = absorbed
        if actor.resources.get("ward", 0) == 0:
            actor.bond_flags["ward_broken"] = True

    def clear_class_combat_resources(self, actor) -> None:
        clear_class_combat_state(actor)

    def is_warrior_actor(self, actor) -> bool:
        return "warrior_grit" in getattr(actor, "features", [])

    def warrior_grit_max(self, actor) -> int:
        return self.class_resource_max(actor, "grit")

    def prepare_warrior_grit_for_combat(self, actor) -> None:
        self.prepare_class_resources_for_combat(actor)

    def grant_warrior_grit(self, actor, amount: int = 1, *, source: str = "") -> int:
        return self.grant_class_resource(actor, "grit", amount, source=source)

    def maybe_gain_grit_from_strong_hit(self, attacker, margin: int) -> None:
        if margin >= 5:
            self.grant_warrior_grit(attacker, source="a strong hit")

    def effective_stability(self, actor) -> int:
        total = actor.ability_mod("STR")
        for bonuses in (actor.equipment_bonuses, actor.gear_bonuses, actor.relationship_bonuses):
            total += int(bonuses.get("stability", 0))
            total += int(bonuses.get("stability_bonus", 0))
        total += self.status_value(actor, "stability_bonus")
        total -= self.status_value(actor, "stability_penalty")
        if self.has_status(actor, "prone"):
            total -= 2
        if self.has_status(actor, "restrained") or self.has_status(actor, "grappled"):
            total -= 2
        if self.has_status(actor, "stunned") or self.has_status(actor, "paralyzed") or self.has_status(actor, "unconscious"):
            total -= 5
        return total

    def stability_target_number(self, actor) -> int:
        return max(1, 10 + self.effective_stability(actor))

    def stability_target_label(self, target_number: int) -> str:
        return f"Stability {target_number}"

    def combat_defense_summary(self, actor) -> str:
        defense = self.effective_defense_percent(actor, damage_type="slashing")
        avoidance = self.effective_avoidance(actor)
        stability = self.effective_stability(actor)
        return f"Defense {defense}%, Avoidance {avoidance:+d}, Stability {stability:+d}"

    def combat_resource_summary_line(self, actor, *, width: int | None = None) -> str | None:
        resource_lines: list[str] = []
        for resource in CLASS_RESOURCE_ORDER:
            if not self.actor_uses_class_resource(actor, resource):
                continue
            maximum = max(0, int(actor.max_resources.get(resource, self.class_resource_max(actor, resource))))
            current = max(0, int(actor.resources.get(resource, 0)))
            if maximum <= 0 and current <= 0:
                continue
            label = self.class_resource_label(resource)
            color = CLASS_RESOURCE_COLORS.get(resource, "white")
            resource_lines.append(self.format_resource_bar(label, current, maximum, width=width, fill_color=color))
        if not resource_lines:
            return None
        return " | ".join(resource_lines)

    def clear_combat_stance(self, actor) -> None:
        for status in (*STANCE_STATUS_NAMES, "guard_stance"):
            actor.conditions.pop(status, None)

    def current_combat_stance_key(self, actor) -> str:
        for key, status in STANCE_STATUS_BY_KEY.items():
            if self.has_status(actor, status):
                return key
        if self.has_status(actor, "guard_stance"):
            return "guard"
        return "neutral"

    def combat_stance_label(self, actor) -> str:
        return STANCE_LABELS[self.current_combat_stance_key(actor)]

    def combat_stance_option(self, stance_key: str, actor) -> str:
        label = STANCE_LABELS[stance_key]
        active = "active" if self.current_combat_stance_key(actor) == stance_key else STANCE_SUMMARIES[stance_key]
        return f"{label} ({active})"

    def set_combat_stance(self, actor, stance_key: str, *, announce: bool = True) -> bool:
        stance_key = stance_key.lower().strip()
        if stance_key not in STANCE_LABELS:
            return False
        previous = self.current_combat_stance_key(actor)
        if stance_key == previous:
            if announce:
                self.say(f"{self.style_name(actor)} keeps {STANCE_LABELS[stance_key]} Stance.")
            return False
        self.clear_combat_stance(actor)
        if stance_key != "neutral":
            actor.conditions[STANCE_STATUS_BY_KEY[stance_key]] = 99
        if announce:
            self.say(f"{self.style_name(actor)} shifts into {STANCE_LABELS[stance_key]} Stance: {STANCE_SUMMARIES[stance_key]}")
        self.apply_stance_upgrade_hooks(actor, stance_key)
        return True

    def use_guard_stance(self, actor) -> None:
        self.set_combat_stance(actor, "guard", announce=False)
        self.say(
            f"{self.style_name(actor)} sets a guarded lane: +20% Defense, +1 Avoidance, +2 Stability, and -2 Accuracy while the stance holds."
        )

    def can_raise_shield(self, actor) -> bool:
        return bool(getattr(actor, "shield", False)) and not self.has_status(actor, "raised_shield")

    def use_raise_shield(self, actor) -> None:
        self.apply_status(actor, "raised_shield", 2, source=f"{actor.name}'s raised shield")
        defense = self.raised_shield_defense_percent(actor)
        self.say(f"{self.style_name(actor)} raises a shield and gains +{defense}% Defense until their next turn.")

    def use_weapon_read(self, actor, target) -> None:
        defense = self.effective_defense_percent(target, damage_type="slashing")
        avoidance = self.effective_avoidance(target)
        stability = self.effective_stability(target)
        armor_break = self.total_armor_break_percent(target)
        defense_band = "high" if defense >= 35 else "low" if defense <= 10 else "moderate"
        avoidance_band = "high" if avoidance >= 4 else "low" if avoidance <= 0 else "moderate"
        stability_band = "high" if stability >= 4 else "low" if stability <= 0 else "moderate"
        answer = "Armor Break or save pressure"
        if avoidance_band == "high" and defense_band != "high":
            answer = "accuracy pressure, marks, or forced saves"
        elif defense_band == "low":
            answer = "plain weapon wounds"
        elif stability_band == "low":
            answer = "shove, prone, or pin pressure"
        break_text = f", Armor Break {armor_break}%" if armor_break else ""
        self.say(
            f"Weapon Read: {self.style_name(target)} has {defense_band} Defense ({defense}%), "
            f"{avoidance_band} Avoidance ({avoidance:+d}), and {stability_band} Stability ({stability:+d}){break_text}. "
            f"Best answer: {answer}."
        )

    def class_stance_upgrade_payload(self, actor, stance_key: str) -> dict[str, object]:
        upgrades = getattr(actor, "bond_flags", {}).get("stance_upgrades", {})
        if not isinstance(upgrades, dict):
            return {}
        payload = upgrades.get(stance_key) or upgrades.get("*") or {}
        return dict(payload) if isinstance(payload, dict) else {}

    def apply_stance_upgrade_hooks(self, actor, stance_key: str) -> None:
        payload = self.class_stance_upgrade_payload(actor, stance_key)
        if not payload:
            return
        for status, duration in dict(payload.get("statuses", {})).items():
            self.apply_status(actor, str(status), int(duration), source=f"{STANCE_LABELS[stance_key]} upgrade")
        for resource, amount in dict(payload.get("resources", {})).items():
            self.grant_class_resource(actor, str(resource), int(amount), source=f"{STANCE_LABELS[stance_key]} upgrade")

    def mark_class_target(self, actor, target, *, mark_key: str = "rogue_mark", duration: int = 2) -> None:
        target.bond_flags[f"{mark_key}_by"] = actor.name
        self.apply_status(target, "marked", duration, source=f"{actor.name}'s mark")

    def target_is_marked_by(self, actor, target, *, mark_key: str = "rogue_mark") -> bool:
        return target.bond_flags.get(f"{mark_key}_by") == actor.name

    def add_rogue_poison_stack(self, actor, target, amount: int = 1, *, duration: int = 2) -> int:
        stacks_by_actor = target.bond_flags.setdefault("rogue_poison_stacks", {})
        if not isinstance(stacks_by_actor, dict):
            stacks_by_actor = {}
            target.bond_flags["rogue_poison_stacks"] = stacks_by_actor
        previous = max(0, int(stacks_by_actor.get(actor.name, 0)))
        stacks_by_actor[actor.name] = min(9, previous + max(0, amount))
        self.apply_status(target, "poisoned", duration, source=f"{actor.name}'s poison")
        return int(stacks_by_actor[actor.name])

    def rogue_poison_stacks(self, actor, target) -> int:
        stacks_by_actor = target.bond_flags.get("rogue_poison_stacks", {})
        if not isinstance(stacks_by_actor, dict):
            return 0
        return max(0, int(stacks_by_actor.get(actor.name, 0)))

    def spend_rogue_satchel(self, actor, amount: int = 1) -> bool:
        return self.spend_class_resource(actor, "satchel", amount)

    def rogue_target_is_exposed(self, actor, target, allies: list | None = None) -> bool:
        if self.has_status(actor, "invisible"):
            return True
        if self.target_is_marked_by(actor, target):
            return True
        exposed_statuses = ("marked", "prone", "restrained", "reeling", "blinded", "poisoned", "armor_broken")
        if any(self.has_status(target, status) for status in exposed_statuses):
            return True
        if allies is not None and any(ally is not actor and ally.is_conscious() for ally in allies):
            return True
        return False

    def can_use_class_reaction(self, actor) -> bool:
        current_round = int(getattr(self, "_active_round_number", 0) or 0)
        return int(actor.bond_flags.get("class_reaction_used_round", -1)) != current_round

    def spend_class_reaction(self, actor, *, source: str = "") -> bool:
        if not self.can_use_class_reaction(actor):
            return False
        actor.bond_flags["class_reaction_used_round"] = int(getattr(self, "_active_round_number", 0) or 0)
        if source:
            actor.bond_flags["class_reaction_source"] = source
        return True

    def trigger_on_hit_hooks(
        self,
        attacker,
        target,
        *,
        actual_damage: int,
        margin: int,
        critical_hit: bool,
        heroes: list | None = None,
        enemies: list | None = None,
    ) -> None:
        if self.actor_uses_class_resource(attacker, "edge") and self.rogue_target_is_exposed(attacker, target, heroes):
            self.grant_class_resource(attacker, "edge", source="an exposed hit")
        if self.target_is_marked_by(attacker, target):
            target.bond_flags["class_mark_last_hit_by"] = attacker.name

    def trigger_on_wound_hooks(self, attacker, target, result: DamageResolution) -> None:
        if self.target_is_marked_by(attacker, target):
            target.bond_flags["class_mark_last_wounded_by"] = attacker.name
            self.grant_class_resource(attacker, "edge", source="a marked Wound")
        if self.actor_uses_class_resource(attacker, "toxin") and self.has_status(target, "poisoned"):
            self.grant_class_resource(attacker, "toxin", source="poison riding a Wound")

    def trigger_damage_resolution_hooks(self, target, source_actor, *, damage_type: str) -> None:
        result = self.last_damage_resolution()
        if result.glance:
            self.grant_warrior_grit(target, source="turning a hit into a Glance")
        elif result.wound:
            self.grant_warrior_grit(target, source="taking a Wound")
        if source_actor is not None and result.wound:
            self.trigger_on_wound_hooks(source_actor, target, result)

    def use_warrior_shove(self, actor, target) -> None:
        if not self.can_make_hostile_action(actor):
            self.say(f"{self.style_name(actor)} can't force the issue while Charmed.")
            return
        target_number = self.stability_target_number(target)
        total_modifier = (
                actor.ability_mod("STR")
                + actor.proficiency_bonus
                + actor.equipment_bonuses.get("attack", 0)
                + actor.gear_bonuses.get("attack", 0)
                + actor.relationship_bonuses.get("attack", 0)
                + self.status_accuracy_modifier(actor)
            )
        d20 = self.roll_check_d20(
            actor,
            self.d20_disadvantage_state(actor, attack=True),
            target_number=target_number,
            target_label=self.stability_target_label(target_number),
            modifier=total_modifier,
            style="attack",
            outcome_kind="attack",
            context_label=f"{actor.name} shoves {target.name}",
        )
        total = d20.kept + total_modifier
        if d20.kept == 1 or (d20.kept != 20 and total < target_number):
            self.say(f"{self.style_name(actor)} shoves into {self.style_name(target)}, but the footing holds.")
            return
        margin = total - target_number
        self.apply_status(target, "prone", 1, source=f"{actor.name}'s shove")
        self.say(f"{self.style_name(actor)} breaks {self.style_name(target)}'s footing with a shove.")
        if margin >= 5 and target.is_conscious():
            self.apply_status(target, "reeling", 1, source=f"{actor.name}'s shove")
            self.grant_warrior_grit(actor, source="a strong shove")

    def perform_weapon_attack(self, attacker, target, heroes, enemies, dodging, *, use_smite: bool = False) -> None:
        if not self.can_make_hostile_action(attacker):
            self.say(f"{self.style_name(attacker)} can't bring themselves to make a hostile move while Charmed.")
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(attacker)
        weapon_item = self.equipped_weapon_item(attacker)
        try:
            advantage = self.attack_advantage_state(attacker, target, heroes, enemies, dodging, ranged=attacker.weapon.ranged)
            target_number = self.effective_attack_target_number(target)
            total_modifier = (
                attacker.attack_bonus()
                + self.ally_pressure_bonus(attacker, heroes, ranged=attacker.weapon.ranged)
                + self.status_accuracy_modifier(attacker)
            )
            d20 = self.roll_check_d20(
                attacker,
                advantage,
                target_number=target_number,
                target_label=self.attack_target_label(target_number),
                modifier=total_modifier,
                style="attack",
                outcome_kind="attack",
                context_label=f"{attacker.name} attacks {target.name}",
            )
            total = d20.kept + total_modifier
            if d20.kept == 1:
                self.say(f"{self.style_name(attacker)} misses {self.style_name(target)} outright.")
                return
            critical_hit = d20.kept >= self.critical_threshold(attacker)
            if critical_hit and target.gear_bonuses.get("crit_immunity", 0):
                critical_hit = False
                self.say(f"{self.style_name(target)}'s armor turns a critical hit into a normal one.")
            if not critical_hit and total < target_number:
                self.say(f"{self.style_name(attacker)} attacks {self.style_name(target)} but misses {self.attack_target_label(target_number)}.")
                return
            self.maybe_gain_grit_from_strong_hit(attacker, total - target_number)
            damage_bonus = attacker.damage_bonus() + self.status_damage_modifier(attacker)
            damage_roll = self.roll_with_display_bonus(
                attacker.weapon.damage,
                bonus=damage_bonus,
                critical=critical_hit,
                style="damage",
                context_label=f"{attacker.name} weapon damage",
                outcome_kind="damage",
            )
            weapon_damage = damage_roll.total + damage_bonus
            weapon_damage_type = weapon_item.damage_type if weapon_item is not None else ""
            if attacker.class_name == "Rogue" and advantage >= 0 and self.can_sneak_attack(attacker, heroes, target):
                sneak = self.roll_with_animation_context(
                    self.rogue_sneak_attack_dice(attacker),
                    critical=critical_hit,
                    style="damage",
                    context_label=f"{attacker.name} Veilstrike",
                    outcome_kind="damage",
                )
                weapon_damage += sneak.total
                self.say(f"Veilstrike adds {self.style_damage(sneak.total)} damage.")
            martial_bonus = None
            smite = None
            if use_smite and attacker.class_name == "Paladin":
                if not self.spend_mp_for_spell(attacker, "divine_smite", "Divine Smite"):
                    self.say(f"{self.style_name(attacker)} reaches for oathfire, but the light will not answer.")
                else:
                    smite = self.roll_with_animation_context(
                        "2d8",
                        critical=critical_hit,
                        style="damage",
                        context_label=spell_label("divine_smite"),
                        outcome_kind="damage",
                    )
                    self.say(f"{spell_label('divine_smite')} adds {self.style_damage(smite.total)} radiant damage.")
            if attacker.archetype == "rukhar" and any(enemy.is_conscious() and enemy is not attacker for enemy in enemies):
                martial_bonus = self.roll_with_animation_context(
                    "2d6",
                    style="damage",
                    context_label=f"{attacker.name} martial edge",
                    outcome_kind="damage",
                )
                weapon_damage += martial_bonus.total
                self.say(f"{self.style_name(attacker)}'s martial edge adds {self.style_damage(martial_bonus.total)} damage.")
            total_actual = self.apply_damage(
                target,
                max(1, weapon_damage),
                damage_type=weapon_damage_type,
                source_actor=attacker,
                apply_defense=True,
            )
            if smite is not None:
                total_actual += self.apply_damage(target, smite.total, damage_type="radiant", source_actor=attacker)
            if weapon_item is not None and weapon_item.extra_damage_dice:
                extra = self.roll_with_animation_context(
                    weapon_item.extra_damage_dice,
                    critical=critical_hit,
                    style="damage",
                    context_label=f"{weapon_item.enchantment or weapon_item.name} bonus damage",
                    outcome_kind="damage",
                )
                extra_actual = self.apply_damage(target, extra.total, damage_type=weapon_item.extra_damage_type, source_actor=attacker, apply_defense=True)
                total_actual += extra_actual
                self.say(
                    f"{weapon_item.enchantment or weapon_item.name} adds {self.style_damage(extra_actual)} "
                    f"{weapon_item.extra_damage_type or 'magic'} damage."
                )
            if critical_hit and weapon_item is not None and weapon_item.crit_extra_damage_dice:
                vicious = self.roll_with_animation_context(
                    weapon_item.crit_extra_damage_dice,
                    style="damage",
                    context_label=f"{weapon_item.enchantment or weapon_item.name} critical damage",
                    outcome_kind="damage",
                )
                vicious_actual = self.apply_damage(target, vicious.total, damage_type=weapon_damage_type, source_actor=attacker, apply_defense=True)
                total_actual += vicious_actual
                self.say(f"{weapon_item.enchantment or weapon_item.name} tears in for {self.style_damage(vicious_actual)} extra critical damage.")
            if total_actual <= 0 and self.last_damage_was_glance():
                self.say(f"{self.style_name(attacker)} hits {self.style_name(target)}, but the blow glances off their Defense.")
            else:
                self.say(f"{self.style_name(attacker)} hits {self.style_name(target)} for {self.style_damage(total_actual)} damage.")
            self.announce_downed_target(target)
            self.trigger_on_hit_hooks(
                attacker,
                target,
                actual_damage=total_actual,
                margin=total - target_number,
                critical_hit=critical_hit,
                heroes=heroes,
                enemies=enemies,
            )
            if total_actual > 0 and attacker.archetype in {"rukhar", "varyn"}:
                self.apply_poison_on_hit(attacker, target)
            if attacker.weapon.ranged or "bow" in attacker.weapon.name.lower():
                self.trigger_blacklake_adjudicator_reflection(attacker, target, source=attacker.weapon.name)
                return
            if d20.kept >= 18 and target.is_conscious():
                self.apply_status(target, "reeling", 1, source=attacker.name)
        finally:
            self.break_invisibility_from_hostile_action(attacker)

    def perform_enemy_attack(self, attacker, target, heroes, enemies, dodging) -> bool:
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(attacker)
        weapon_item = self.equipped_weapon_item(attacker)
        target_had_positive_status = self.hero_has_positive_combat_status(target)
        target_had_blessing = any(self.has_status(target, status) for status in ("blessed", "emboldened"))
        advantage = self.attack_advantage_state(attacker, target, heroes, enemies, dodging, ranged=attacker.weapon.ranged)
        target_number = self.effective_attack_target_number(target)
        total_modifier = (
            attacker.attack_bonus()
            + self.ally_pressure_bonus(attacker, enemies, ranged=attacker.weapon.ranged)
            + self.status_accuracy_modifier(attacker)
        )
        d20 = self.roll_check_d20(
            attacker,
            advantage,
            target_number=target_number,
            target_label=self.attack_target_label(target_number),
            modifier=total_modifier,
            style="attack",
            outcome_kind="attack",
            context_label=f"{attacker.name} attacks {target.name}",
        )
        total = d20.kept + total_modifier
        critical_hit = d20.kept == 20 and not target.gear_bonuses.get("crit_immunity", 0)
        if d20.kept == 1 or (not critical_hit and d20.kept != 20 and total < target_number):
            self.say(f"{self.style_name(attacker)} fails to land a hit on {self.style_name(target)}.")
            return False
        if d20.kept == 20 and not critical_hit:
            self.say(f"{self.style_name(target)}'s armor blunts what would have been a critical strike.")
        damage_bonus = attacker.damage_bonus() + self.status_damage_modifier(attacker)
        damage_roll = self.roll_with_display_bonus(
            attacker.weapon.damage,
            bonus=damage_bonus,
            critical=critical_hit,
            style="damage",
            context_label=f"{attacker.name} weapon damage",
            outcome_kind="damage",
        )
        damage = max(1, damage_roll.total + damage_bonus)
        if self.has_status(target, "marked"):
            damage += 2
            self.say(f"The ember mark on {target.name} flares and gives {attacker.name} a cleaner wound to drive into.")
        actual = self.apply_damage(
            target,
            damage,
            damage_type=weapon_item.damage_type if weapon_item is not None else "",
            source_actor=attacker,
            apply_defense=True,
        )
        if actual <= 0 and self.last_damage_was_glance():
            self.say(f"{self.style_name(attacker)} hits {self.style_name(target)}, but the blow glances off their Defense.")
        else:
            self.say(f"{self.style_name(attacker)} hits {self.style_name(target)} for {self.style_damage(actual)} damage.")
        self.announce_downed_target(target)
        self.trigger_on_hit_hooks(
            attacker,
            target,
            actual_damage=actual,
            margin=total - target_number,
            critical_hit=critical_hit,
            heroes=enemies,
            enemies=heroes,
        )
        if attacker.archetype == "resonance_leech" and target.is_conscious():
            if any(self.has_status(target, status) for status in ("frightened", "reeling", "deafened")):
                extra = self.apply_damage(
                    target,
                    self.roll_with_display_bonus(
                        "1d6",
                        style="damage",
                        context_label=f"{attacker.name}'s echo feast",
                        outcome_kind="damage",
                    ).total,
                    damage_type="psychic",
                )
                self.say(f"{attacker.name} feeds on the broken cadence for {self.style_damage(extra)} extra psychic damage.")
                self.announce_downed_target(target)
        if attacker.archetype == "pact_archive_warden":
            self.apply_status(attacker, "guarded", 1, source=f"{attacker.name}'s custody protocol")
        if attacker.archetype == "survey_chain_revenant" and target.is_conscious() and self.has_status(target, "grappled"):
            self.apply_status(attacker, "guarded", 1, source=f"{attacker.name}'s unfinished shift")
        if attacker.archetype == "censer_horror" and target.is_conscious() and self.has_status(target, "frightened"):
            extra = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    "1d4",
                    style="damage",
                    context_label=f"{attacker.name}'s cinder liturgy",
                    outcome_kind="damage",
                ).total,
                damage_type="fire",
            )
            self.say(f"{attacker.name}'s cinder liturgy bites into the panic for {self.style_damage(extra)} extra fire damage.")
            self.announce_downed_target(target)
        if attacker.archetype == "memory_taker_adept" and target_had_positive_status and not attacker.bond_flags.get("borrowed_instinct_used"):
            attacker.bond_flags["borrowed_instinct_used"] = True
            self.apply_status(attacker, "emboldened", 2, source=f"{attacker.name}'s borrowed instinct")
        if attacker.archetype == "covenant_breaker_wight" and target_had_blessing:
            current_round = int(getattr(self, "_active_round_number", 0) or 0)
            if int(attacker.bond_flags.get("life_levy_round", -1)) != current_round:
                attacker.bond_flags["life_levy_round"] = current_round
                healed = attacker.heal(6)
                if healed > 0:
                    self.say(f"{attacker.name} levies life from the broken vow and regains {self.style_healing(healed)} hit points.")
        if attacker.archetype == "hollowed_survey_titan" and attacker.current_hp * 2 > attacker.max_hp:
            self.apply_status(attacker, "guarded", 1, source=f"{attacker.name}'s loadbearing frame")
        if attacker.archetype == "ashstone_percher" and attacker.resources.get("drop_strike", 0) > 0 and target.is_conscious():
            attacker.resources["drop_strike"] = 0
            extra = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    "1d4",
                    style="damage",
                    context_label=f"{attacker.name} drop strike",
                    outcome_kind="damage",
                ).total,
                damage_type="slashing",
            )
            self.say(f"{attacker.name} crashes down from above for {self.style_damage(extra)} extra slashing damage.")
            self.announce_downed_target(target)
        if attacker.archetype == "bugbear_reaver" and attacker.resources.get("surprise_attack", 0) > 0 and target.is_conscious():
            attacker.resources["surprise_attack"] = 0
            extra = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    "2d6",
                    critical=critical_hit,
                    style="damage",
                    context_label=f"{attacker.name} ambush damage",
                    outcome_kind="damage",
                ).total,
                damage_type="bludgeoning",
            )
            self.say(f"{attacker.name} turns the first clean opening into {self.style_damage(extra)} extra ambush damage.")
            self.announce_downed_target(target)
        if attacker.archetype in {"wolf", "worg"} and target.is_conscious():
            if not self.saving_throw(target, "STR", 11, context=f"against {attacker.name}'s mauling rush"):
                self.apply_status(target, "prone", 1, source=attacker.name)
        if attacker.archetype == "briar_twig" and target.is_conscious():
            if not self.saving_throw(target, "STR", 11, context=f"against {attacker.name}'s snagging thorns"):
                self.apply_status(target, "reeling", 2, source=f"{attacker.name}'s snagging thorns")
        if actual > 0 and attacker.archetype == "carrion_stalker" and target.is_conscious():
            self.apply_status(target, "bleeding", 2, source=f"{attacker.name}'s serrated talons")
        if attacker.archetype == "bandit" and d20.kept >= 18 and target.is_conscious():
            if not self.saving_throw(target, "STR", 11, context=f"against {attacker.name}'s clinch"):
                self.apply_status(target, "grappled", 1, source=attacker.name)
        if attacker.archetype == "acidmaw_burrower" and target.is_conscious():
            if not self.saving_throw(target, "STR", 12, context=f"against {attacker.name}'s burrowing clamp"):
                self.apply_status(target, "grappled", 1, source=f"{attacker.name}'s burrowing clamp")
        if attacker.archetype == "rust_shell_scuttler" and target.is_conscious():
            if self.has_status(target, "acid"):
                extra = self.apply_damage(
                    target,
                    self.roll_with_display_bonus(
                        "1d4",
                        style="damage",
                        context_label=f"{attacker.name} acid bite",
                        outcome_kind="damage",
                    ).total,
                    damage_type="acid",
                )
                self.say(f"{attacker.name} worries an already-corroded weak point for {self.style_damage(extra)} extra acid damage.")
                self.announce_downed_target(target)
            self.apply_status(target, "acid", 2, source=f"{attacker.name}'s rust-bite")
        if attacker.archetype == "ogre_brute" and d20.kept >= 18 and target.is_conscious():
            if not self.saving_throw(target, "STR", 12, context=f"against {attacker.name}'s club smash"):
                self.apply_status(target, "prone", 1, source=attacker.name)
        if attacker.archetype == "nothic" and d20.kept >= 18 and target.is_conscious():
            if not self.saving_throw(target, "WIS", 12, context=f"against {attacker.name}'s invasive whisper"):
                self.apply_status(target, "frightened", 1, source=attacker.name)
        if actual > 0 and attacker.archetype in {"rukhar", "varyn", "mireweb_spider", "ettervine_webherd", "duskmire_matriarch"}:
            self.apply_poison_on_hit(attacker, target)
        if attacker.archetype == "cache_mimic" and target.is_conscious():
            if attacker.resources.get("adhesive_grab", 0) > 0:
                attacker.resources["adhesive_grab"] = 0
            if not self.saving_throw(target, "STR", 13, context=f"against {attacker.name}'s adhesive bite"):
                self.apply_status(target, "grappled", 2, source=f"{attacker.name}'s adhesive bite")
        if attacker.archetype == "stonegaze_skulker" and target.is_conscious() and self.has_status(target, "restrained"):
            extra = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    "1d4",
                    style="damage",
                    context_label=f"{attacker.name} venom",
                    outcome_kind="damage",
                ).total,
                damage_type="poison",
            )
            self.say(f"{attacker.name}'s mineral venom bites deeper for {self.style_damage(extra)} poison damage.")
            self.announce_downed_target(target)
        if attacker.archetype == "grimlock_tunneler" and target.is_conscious():
            if self.has_status(target, "reeling") or d20.kept >= 18:
                if not self.saving_throw(target, "STR", 12, context=f"against {attacker.name}'s hooked drag"):
                    self.apply_status(target, "grappled", 2, source=f"{attacker.name}'s hooked drag")
        if attacker.archetype == "hookclaw_burrower" and target.is_conscious():
            if not self.saving_throw(target, "STR", 14, context=f"against {attacker.name}'s cave drag"):
                already_grappled = self.has_status(target, "grappled")
                self.apply_status(target, "grappled", 2, source=f"{attacker.name}'s cave drag")
                if already_grappled:
                    self.apply_status(target, "prone", 1, source=f"{attacker.name}'s cave drag")
        if attacker.archetype == "stirge_swarm" and target.is_conscious():
            attacker.bond_flags["attached_to"] = target.name
            self.apply_status(target, "grappled", 2, source=f"{attacker.name}'s feeding swarm")
            self.say(f"{attacker.name} latches onto {target.name} and begins feeding.")
        if attacker.archetype == "ochre_slime" and target.is_conscious():
            acid = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    "1d4",
                    style="damage",
                    context_label=f"{attacker.name} corrosive slime",
                    outcome_kind="damage",
                ).total,
                damage_type="acid",
            )
            self.say(f"{attacker.name}'s dripping pseudopod burns for an extra {self.style_damage(acid)} acid damage.")
            self.apply_status(target, "acid", 2, source=f"{attacker.name}'s corrosive slime")
            self.announce_downed_target(target)
        if attacker.archetype == "animated_armor" and target.is_conscious() and d20.kept >= 18:
            if not self.saving_throw(target, "STR", 13, context=f"against {attacker.name}'s driving slam"):
                self.apply_status(target, "prone", 1, source=f"{attacker.name}'s driving slam")
        if attacker.archetype == "cliff_harpy" and target.is_conscious() and attacker.resources.get("swoop", 0) > 0:
            attacker.resources["swoop"] = 0
            if not self.saving_throw(target, "STR", 12, context=f"against {attacker.name}'s swooping pass"):
                self.apply_status(target, "prone", 1, source=f"{attacker.name}'s swoop")
        if attacker.archetype == "whispermaw_blob" and target.is_conscious() and d20.kept >= 18:
            if not self.saving_throw(target, "STR", 13, context=f"against {attacker.name}'s warped bulk"):
                self.apply_status(target, "prone", 1, source=f"{attacker.name}'s warped bulk")
        if attacker.archetype == "blacklake_pincerling" and target.is_conscious():
            if not self.saving_throw(target, "STR", 13, context=f"against {attacker.name}'s pincer hold"):
                self.apply_status(target, "grappled", 2, source=f"{attacker.name}'s pincer hold")
        if attacker.archetype == "thunderroot_mound" and target.is_conscious():
            if not self.saving_throw(target, "STR", 14, context=f"against {attacker.name}'s grasping roots"):
                self.apply_status(target, "restrained", 2, source=f"{attacker.name}'s grasping roots")
        if attacker.archetype == "oathbroken_revenant" and target.is_conscious():
            if target.name == str(attacker.bond_flags.get("marked_target", "")):
                extra = self.apply_damage(
                    target,
                    self.roll_with_display_bonus(
                        "1d6",
                        style="damage",
                        context_label=f"{attacker.name}'s vendetta",
                        outcome_kind="damage",
                    ).total,
                    damage_type="necrotic",
                )
                self.say(f"{attacker.name}'s vendetta cuts deeper for {self.style_damage(extra)} necrotic damage.")
                self.announce_downed_target(target)
        if attacker.archetype == "choir_executioner" and target.is_conscious():
            if any(self.has_status(target, status) for status in ("frightened", "restrained", "incapacitated")):
                extra = self.apply_damage(
                    target,
                    self.roll_with_display_bonus(
                        "2d6",
                        style="damage",
                        context_label=f"{attacker.name}'s execution strike",
                        outcome_kind="damage",
                    ).total,
                    damage_type="slashing",
                )
                self.say(f"{attacker.name} turns the opening into {self.style_damage(extra)} extra execution damage.")
                self.announce_downed_target(target)
        if attacker.archetype == "lantern_fen_wisp" and target.is_conscious() and attacker.resources.get("vanish", 0) > 0 and attacker.current_hp <= attacker.max_hp // 2:
            attacker.resources["vanish"] = 0
            self.apply_status(attacker, "invisible", 1, source=f"{attacker.name}'s vanish")
        return True

    def cast_sacred_flame(self, caster, target) -> None:
        channel = spell_label("sacred_flame")
        if not self.can_make_hostile_action(caster):
            self.say(f"{self.style_name(caster)} hesitates and cannot turn {channel} on an enemy while Charmed.")
            return
        if not self.spend_mp_for_spell(caster, "sacred_flame", "Sacred Flame"):
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(caster)
        dc = 8 + caster.proficiency_bonus + caster.ability_mod("WIS")
        success = self.saving_throw(target, "DEX", dc, context=f"against {channel}")
        if success:
            self.say(f"{self.style_name(target)} slips clear of the radiant burst.")
            return
        actual = self.apply_damage(
            target,
            self.roll_with_display_bonus(
                "1d8",
                bonus=self.spell_damage_bonus(caster),
                style="damage",
                context_label=channel,
                outcome_kind="damage",
            ).total
            + self.spell_damage_bonus(caster),
            source_actor=caster,
        )
        self.say(f"{channel} burns {self.style_name(target)} for {self.style_damage(actual)} radiant damage.")
        self.announce_downed_target(target)
        self.trigger_blacklake_adjudicator_reflection(caster, target, source=channel)
        if target.is_conscious():
            self.apply_status(target, "reeling", 1, source="radiant force")

    def cast_cure_wounds(self, caster, target) -> None:
        channel = spell_label("cure_wounds")
        if not self.spend_mp_for_spell(caster, "cure_wounds", "Cure Wounds"):
            return
        ability = "CHA" if caster.class_name in {"Bard", "Paladin"} else "WIS"
        amount = self.roll_with_animation_context(
            "1d8",
            style="healing",
            context_label=channel,
            outcome_kind="healing",
        ).total + caster.ability_mod(ability) + self.healing_bonus(caster)
        healed = target.heal(max(1, amount))
        play_heal_sound_for = getattr(self, "play_heal_sound_for", None)
        if healed > 0 and callable(play_heal_sound_for):
            play_heal_sound_for(caster)
        self.say(f"{self.style_name(caster)} restores {self.style_healing(healed)} hit points to {self.style_name(target)}.")

    def cast_healing_word(self, caster, target) -> None:
        channel = spell_label("healing_word")
        if not self.spend_mp_for_spell(caster, "healing_word", "Healing Word"):
            return
        ability = "CHA" if caster.class_name == "Bard" else "WIS"
        amount = self.roll_with_animation_context(
            "1d4",
            style="healing",
            context_label=channel,
            outcome_kind="healing",
        ).total + caster.ability_mod(ability) + self.healing_bonus(caster)
        healed = target.heal(max(1, amount))
        play_heal_sound_for = getattr(self, "play_heal_sound_for", None)
        if healed > 0 and callable(play_heal_sound_for):
            play_heal_sound_for(caster)
        self.say(f"{self.style_name(caster)} sends {channel} across the line and restores {self.style_healing(healed)} hit points to {self.style_name(target)}.")

    def cast_fire_bolt(self, caster, target, dodging) -> None:
        channel = spell_label("fire_bolt")
        if not self.can_make_hostile_action(caster):
            self.say(f"{self.style_name(caster)} cannot channel {channel} at an enemy while Charmed.")
            return
        if not self.spend_mp_for_spell(caster, "fire_bolt", "Fire Bolt"):
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(caster)
        try:
            attack_bonus = self.spell_attack_bonus(caster, "INT")
            advantage = self.attack_advantage_state(caster, target, self.state.party_members(), [target], dodging, ranged=True)
            target_number = self.effective_attack_target_number(target)
            total_modifier = (
                attack_bonus
                + self.ally_pressure_bonus(caster, self.state.party_members(), ranged=True)
                + self.status_accuracy_modifier(caster)
            )
            d20 = self.roll_check_d20(
                caster,
                advantage,
                target_number=target_number,
                target_label=self.attack_target_label(target_number),
                modifier=total_modifier,
                style="attack",
                outcome_kind="attack",
                context_label=f"{caster.name} channels {channel}",
            )
            total = d20.kept + total_modifier
            if d20.kept == 1 or (d20.kept != 20 and total < target_number):
                self.say(f"{self.style_name(caster)}'s {channel} misses {self.style_name(target)}.")
                return
            actual = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    "1d10",
                    bonus=self.spell_damage_bonus(caster),
                    critical=d20.kept == 20,
                    style="damage",
                    context_label=f"{channel} damage",
                    outcome_kind="damage",
                ).total
                + self.spell_damage_bonus(caster),
                source_actor=caster,
            )
            self.say(f"{channel} scorches {self.style_name(target)} for {self.style_damage(actual)} fire damage.")
            self.announce_downed_target(target)
            self.trigger_blacklake_adjudicator_reflection(caster, target, source=channel)
            if target.is_conscious():
                self.apply_status(target, "burning", 2, source=channel)
        finally:
            self.break_invisibility_from_hostile_action(caster)

    def cast_produce_flame(self, caster, target, dodging) -> None:
        channel = spell_label("produce_flame")
        if not self.can_make_hostile_action(caster):
            self.say(f"{self.style_name(caster)} cannot lash out with {channel} while Charmed.")
            return
        if not self.spend_mp_for_spell(caster, "produce_flame", "Produce Flame"):
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(caster)
        try:
            attack_bonus = self.spell_attack_bonus(caster, "WIS")
            advantage = self.attack_advantage_state(caster, target, self.state.party_members(), [target], dodging, ranged=True)
            target_number = self.effective_attack_target_number(target)
            total_modifier = (
                attack_bonus
                + self.ally_pressure_bonus(caster, self.state.party_members(), ranged=True)
                + self.status_accuracy_modifier(caster)
            )
            d20 = self.roll_check_d20(
                caster,
                advantage,
                target_number=target_number,
                target_label=self.attack_target_label(target_number),
                modifier=total_modifier,
                style="attack",
                outcome_kind="attack",
                context_label=f"{caster.name} hurls {channel}",
            )
            total = d20.kept + total_modifier
            if d20.kept == 1 or (d20.kept != 20 and total < target_number):
                self.say(f"{self.style_name(caster)}'s {channel} misses {self.style_name(target)}.")
                return
            actual = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    "1d8",
                    bonus=self.spell_damage_bonus(caster),
                    critical=d20.kept == 20,
                    style="damage",
                    context_label=f"{channel} damage",
                    outcome_kind="damage",
                ).total
                + self.spell_damage_bonus(caster),
                source_actor=caster,
            )
            self.say(f"{channel} sears {self.style_name(target)} for {self.style_damage(actual)} fire damage.")
            self.announce_downed_target(target)
            self.trigger_blacklake_adjudicator_reflection(caster, target, source=channel)
            if target.is_conscious():
                self.apply_status(target, "burning", 2, source=channel)
        finally:
            self.break_invisibility_from_hostile_action(caster)

    def cast_magic_missile(self, caster, target) -> None:
        channel = spell_label("magic_missile")
        if not self.can_make_hostile_action(caster):
            self.say(f"{self.style_name(caster)} cannot direct {channel} at an enemy while Charmed.")
            return
        if not self.spend_mp_for_spell(caster, "magic_missile", "Magic Missile"):
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(caster)
        try:
            dart_count = 3
            actual = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    f"{dart_count}d4+{dart_count}",
                    bonus=self.spell_damage_bonus(caster),
                    style="damage",
                    context_label=channel,
                    outcome_kind="damage",
                ).total
                + self.spell_damage_bonus(caster),
                source_actor=caster,
            )
            self.say(f"{channel} slams into {self.style_name(target)} for {self.style_damage(actual)} force damage.")
            self.announce_downed_target(target)
            self.trigger_blacklake_adjudicator_reflection(caster, target, source=channel)
        finally:
            self.break_invisibility_from_hostile_action(caster)

    def cast_vicious_mockery(self, caster, target) -> None:
        channel = spell_label("vicious_mockery")
        if not self.can_make_hostile_action(caster):
            self.say(f"{self.style_name(caster)} cannot weaponize a cutting remark while Charmed.")
            return
        if not self.spend_mp_for_spell(caster, "vicious_mockery", "Vicious Mockery"):
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(caster)
        try:
            dc = 8 + caster.proficiency_bonus + caster.ability_mod("CHA")
            success = self.saving_throw(target, "WIS", dc, context=f"against {channel}")
            if success:
                self.say(f"{self.style_name(target)} bites back a wince and resists the cadence.")
                return
            actual = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    "1d6",
                    bonus=self.spell_damage_bonus(caster),
                    style="damage",
                    context_label=channel,
                    outcome_kind="damage",
                ).total
                + self.spell_damage_bonus(caster),
                damage_type="psychic",
                source_actor=caster,
            )
            self.say(f"{self.style_name(caster)}'s {channel} rattles {self.style_name(target)} for {self.style_damage(actual)} psychic damage.")
            self.announce_downed_target(target)
            if target.is_conscious():
                self.apply_status(target, "reeling", 2, source=channel)
        finally:
            self.break_invisibility_from_hostile_action(caster)

    def cast_eldritch_blast(self, caster, target, dodging) -> None:
        channel = spell_label("eldritch_blast")
        if not self.can_make_hostile_action(caster):
            self.say(f"{self.style_name(caster)} cannot level {channel} at an enemy while Charmed.")
            return
        if not self.spend_mp_for_spell(caster, "eldritch_blast", "Eldritch Blast"):
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(caster)
        try:
            attack_bonus = self.spell_attack_bonus(caster, "CHA")
            advantage = self.attack_advantage_state(caster, target, self.state.party_members(), [target], dodging, ranged=True)
            target_number = self.effective_attack_target_number(target)
            total_modifier = (
                attack_bonus
                + self.ally_pressure_bonus(caster, self.state.party_members(), ranged=True)
                + self.status_accuracy_modifier(caster)
            )
            d20 = self.roll_check_d20(
                caster,
                advantage,
                target_number=target_number,
                target_label=self.attack_target_label(target_number),
                modifier=total_modifier,
                style="attack",
                outcome_kind="attack",
                context_label=f"{caster.name} channels {channel}",
            )
            total = d20.kept + total_modifier
            if d20.kept == 1 or (d20.kept != 20 and total < target_number):
                self.say(f"{self.style_name(caster)}'s {channel} tears sparks from stone but misses {self.style_name(target)}.")
                return
            actual = self.apply_damage(
                target,
                self.roll_with_display_bonus(
                    "1d10",
                    bonus=self.spell_damage_bonus(caster),
                    critical=d20.kept == 20,
                    style="damage",
                    context_label=f"{channel} damage",
                    outcome_kind="damage",
                ).total
                + self.spell_damage_bonus(caster),
                damage_type="force",
                source_actor=caster,
            )
            self.say(f"{channel} hammers {self.style_name(target)} for {self.style_damage(actual)} force damage.")
            self.announce_downed_target(target)
            self.trigger_blacklake_adjudicator_reflection(caster, target, source=channel)
            if target.is_conscious():
                self.apply_status(target, "reeling", 1, source=f"{channel} impact")
        finally:
            self.break_invisibility_from_hostile_action(caster)

    def use_rage(self, actor) -> None:
        if not actor.spend_resource("rage"):
            self.say(f"{self.style_name(actor)} has no Battle Surge left to draw on.")
            return
        actor.grant_temp_hp(4 + actor.level)
        self.apply_status(actor, "emboldened", 3, source="Battle Surge")
        self.say(f"{self.style_name(actor)} enters Battle Surge, taking {self.style_healing(actor.temp_hp)} temporary hit points with it.")

    def use_bardic_inspiration(self, actor, target) -> None:
        if not actor.spend_resource("bardic_inspiration"):
            self.say(f"{self.style_name(actor)} has no Rally Note left.")
            return
        self.apply_status(target, "blessed", 2, source=f"{actor.name}'s inspiration")
        self.say(f"{self.style_name(actor)} lifts {self.style_name(target)} with a sharp line and steadier rhythm.")

    def use_martial_arts(self, attacker, target, heroes, enemies, dodging) -> None:
        if not self.can_make_hostile_action(attacker):
            self.say(f"{self.style_name(attacker)} cannot lash out with a Close Form strike while Charmed.")
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(attacker)
        try:
            advantage = self.attack_advantage_state(attacker, target, heroes, enemies, dodging, ranged=False)
            target_number = self.effective_attack_target_number(target)
            total_modifier = (
                self.weapon_attack_bonus_for(attacker, attacker.weapon)
                + self.ally_pressure_bonus(attacker, heroes, ranged=False)
                + self.status_accuracy_modifier(attacker)
            )
            d20 = self.roll_check_d20(
                attacker,
                advantage,
                target_number=target_number,
                target_label=self.attack_target_label(target_number),
                modifier=total_modifier,
                style="attack",
                outcome_kind="attack",
                context_label=f"{attacker.name} Close Form strike",
            )
            total = d20.kept + total_modifier
            critical_hit = d20.kept >= self.critical_threshold(attacker)
            if d20.kept == 1 or (not critical_hit and d20.kept != 20 and total < target_number):
                self.say(f"{self.style_name(attacker)}'s Close Form strike misses {self.style_name(target)}.")
                return
            self.maybe_gain_grit_from_strong_hit(attacker, total - target_number)
            damage_bonus = self.weapon_damage_bonus_for(attacker, attacker.weapon) + self.status_damage_modifier(attacker)
            damage_roll = self.roll_with_display_bonus(
                "1d4",
                bonus=damage_bonus,
                critical=critical_hit,
                style="damage",
                context_label=f"{attacker.name} Close Form damage",
                outcome_kind="damage",
            )
            actual = self.apply_damage(
                target,
                max(1, damage_roll.total + damage_bonus),
                damage_type="bludgeoning",
                source_actor=attacker,
                apply_defense=True,
            )
            self.say(f"{self.style_name(attacker)} snaps in with a Close Form strike for {self.style_damage(actual)} damage.")
            if target.is_conscious():
                self.apply_status(target, "reeling", 1, source=attacker.name)
            self.announce_downed_target(target)
        finally:
            self.break_invisibility_from_hostile_action(attacker)

    def use_flurry_of_blows(self, attacker, target, heroes, enemies, dodging) -> None:
        if not attacker.spend_resource("ki"):
            self.say(f"{self.style_name(attacker)} has no focus left for Twinflow Strikes.")
            return
        self.say(f"{self.style_name(attacker)} spends 1 focus and flows into Twinflow Strikes.")
        self.use_martial_arts(attacker, target, heroes, enemies, dodging)
        if target.is_conscious():
            self.use_martial_arts(attacker, target, heroes, enemies, dodging)

    def perform_offhand_attack(self, attacker, target, heroes, enemies, dodging) -> None:
        if not self.can_make_hostile_action(attacker):
            self.say(f"{self.style_name(attacker)} cannot lash out with an off-hand strike while Charmed.")
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(attacker)
        off_hand_item = self.equipped_off_hand_weapon_item(attacker)
        if off_hand_item is None:
            self.say(f"{self.style_name(attacker)} has no off-hand weapon ready.")
            return
        weapon = off_hand_item.weapon
        try:
            advantage = self.attack_advantage_state(attacker, target, heroes, enemies, dodging, ranged=weapon.ranged)
            target_number = self.effective_attack_target_number(target)
            total_modifier = (
                self.weapon_attack_bonus_for(attacker, weapon)
                + self.ally_pressure_bonus(attacker, heroes, ranged=weapon.ranged)
                + self.status_accuracy_modifier(attacker)
            )
            d20 = self.roll_check_d20(
                attacker,
                advantage,
                target_number=target_number,
                target_label=self.attack_target_label(target_number),
                modifier=total_modifier,
                style="attack",
                outcome_kind="attack",
                context_label=f"{attacker.name} off-hand attack",
            )
            total = d20.kept + total_modifier
            critical_hit = d20.kept >= self.critical_threshold(attacker)
            if d20.kept == 1 or (not critical_hit and d20.kept != 20 and total < target_number):
                self.say(f"{self.style_name(attacker)}'s off-hand attack misses {self.style_name(target)}.")
                return
            self.maybe_gain_grit_from_strong_hit(attacker, total - target_number)
            damage_bonus = self.weapon_damage_bonus_for(attacker, weapon, include_ability_mod=False) + self.status_damage_modifier(attacker)
            actual = self.apply_damage(
                target,
                max(
                    1,
                    self.roll_with_display_bonus(
                        weapon.damage,
                        bonus=damage_bonus,
                        critical=critical_hit,
                        style="damage",
                        context_label=f"{attacker.name} off-hand damage",
                        outcome_kind="damage",
                    ).total
                    + damage_bonus,
                ),
                damage_type=off_hand_item.damage_type,
                source_actor=attacker,
                apply_defense=True,
            )
            self.say(f"{self.style_name(attacker)} strikes with {off_hand_item.name} for {self.style_damage(actual)} damage.")
            self.announce_downed_target(target)
        finally:
            self.break_invisibility_from_hostile_action(attacker)

    def use_second_wind(self, actor) -> None:
        if not actor.spend_resource("second_wind"):
            self.say(f"{self.style_name(actor)} has already used Second Breath.")
            return
        amount = self.roll_with_animation_context(
            "1d10",
            style="healing",
            context_label="Second Breath",
            outcome_kind="healing",
        ).total + actor.level
        healed = actor.heal(amount)
        play_heal_sound_for = getattr(self, "play_heal_sound_for", None)
        if healed > 0 and callable(play_heal_sound_for):
            play_heal_sound_for(actor)
        self.say(f"{self.style_name(actor)} steadies themselves and regains {self.style_healing(healed)} hit points.")

    def use_action_surge(self, actor, target, heroes, enemies, dodging) -> None:
        if not actor.spend_resource("action_surge"):
            self.say(f"{self.style_name(actor)} has already spent Battle Surge this rest.")
            return
        self.say(f"{self.style_name(actor)} digs deep and surges into a second strike.")
        self.perform_weapon_attack(actor, target, heroes, enemies, dodging)

    def use_channel_divinity(self, actor, target) -> None:
        if not self.can_make_hostile_action(actor):
            self.say(f"{self.style_name(actor)} cannot invoke hostile Lantern judgment while Charmed.")
            return
        if not actor.spend_resource("channel_divinity"):
            self.say(f"{self.style_name(actor)} has no Lantern Surge remaining.")
            return
        play_attack_sound_for = getattr(self, "play_attack_sound_for", None)
        if callable(play_attack_sound_for):
            play_attack_sound_for(actor)
        actual = self.apply_damage(
            target,
            self.roll_with_display_bonus(
                "2d8",
                bonus=self.spell_damage_bonus(actor),
                style="damage",
                context_label="Lantern Surge",
                outcome_kind="damage",
            ).total
            + self.spell_damage_bonus(actor),
            source_actor=actor,
        )
        self.say(
            f"{self.style_name(actor)} invokes Lantern Surge and sears {self.style_name(target)} "
            f"for {self.style_damage(actual)} radiant damage."
        )
        self.announce_downed_target(target)
        if target.is_conscious():
            self.apply_status(target, "stunned", 1, source="Lantern judgment")

    def help_downed_ally(self, actor, target) -> None:
        success = self.skill_check(actor, "Medicine", 10, context=f"to haul {target.name} back into the fight")
        if success:
            target.current_hp = 1
            target.stable = False
            target.death_successes = 0
            target.death_failures = 0
            play_heal_sound_for = getattr(self, "play_heal_sound_for", None)
            if callable(play_heal_sound_for):
                play_heal_sound_for(actor)
            self.say(
                f"{self.style_name(actor)} gets {self.style_name(target)} back to their feet at "
                f"{self.style_healing(1)} hit point."
            )
            return
        target.stable = True
        target.death_successes = 0
        target.death_failures = 0
        self.say(f"{self.style_name(actor)} stabilizes {self.style_name(target)}, but they cannot stand yet.")

    def use_healing_potion(self, user, target) -> None:
        healing_potion = ITEMS["potion_healing"]
        if not (user.spend_item("Healing Potion") or user.spend_item(healing_potion.name)):
            self.say(f"{self.style_name(user)} fumbles for a healing potion that is no longer there.")
            return
        healed = target.heal(
            self.roll_with_animation_context(
                "2d4+2",
                style="healing",
                context_label=healing_potion.name,
                outcome_kind="healing",
            ).total
        )
        play_heal_sound_for = getattr(self, "play_heal_sound_for", None)
        if healed > 0 and callable(play_heal_sound_for):
            play_heal_sound_for(user)
        self.say(
            f"{self.style_name(user)} uses {healing_potion.name} on {self.style_name(target)}, "
            f"restoring {self.style_healing(healed)} hit points."
        )

    def use_lay_on_hands(self, user, target) -> None:
        pool = user.resources.get("lay_on_hands", 0)
        if pool <= 0:
            self.say(f"{self.style_name(user)} has no Oath Mend healing left.")
            return
        amount = min(pool, 5, target.max_hp - target.current_hp if not target.dead else 0)
        if amount <= 0:
            self.say(f"{self.style_name(target)} does not need healing right now.")
            return
        user.resources["lay_on_hands"] -= amount
        healed = target.heal(amount)
        play_heal_sound_for = getattr(self, "play_heal_sound_for", None)
        if healed > 0 and callable(play_heal_sound_for):
            play_heal_sound_for(user)
        self.say(
            f"{self.style_name(user)} channels oathbound power and restores {self.style_healing(healed)} "
            f"hit points to {self.style_name(target)}."
        )

    def attempt_parley(self, actor, enemies, dc: int) -> None:
        skill = "Persuasion" if actor.skill_bonus("Persuasion") >= actor.skill_bonus("Intimidation") else "Intimidation"
        success = self.skill_check(actor, skill, dc, context="to force a break in the enemy's morale")
        if not success:
            for enemy in enemies:
                if enemy.is_conscious():
                    self.apply_status(enemy, "emboldened", 1, source="defying the parley")
            self.say("The enemy line hardens instead of yielding.")
            return
        leader = next((enemy for enemy in enemies if enemy.is_conscious() and "leader" in enemy.tags), None)
        if leader is not None and leader.current_hp <= leader.max_hp // 2:
            for enemy in enemies:
                if enemy.is_conscious():
                    enemy.current_hp = 0
                    enemy.dead = True
            self.say("The leader's nerve breaks and the rest of the encounter collapses with it.")
            return
        weakest = min((enemy for enemy in enemies if enemy.is_conscious()), key=lambda enemy: enemy.current_hp)
        weakest.current_hp = 0
        weakest.dead = True
        for enemy in enemies:
            if enemy.is_conscious():
                self.apply_status(enemy, "frightened", 1, source="the collapsing line")
        self.say(f"{self.style_name(weakest)} decides this pay is not worth dying for and flees.")

    def attack_advantage_state(self, attacker, target, heroes, enemies, dodging, *, ranged: bool = False) -> int:
        state = 0
        if self.dodge_applies_against_attacker(target, attacker):
            state -= 1
        if "pack_tactics" in getattr(attacker, "features", []) and any(enemy.is_conscious() and enemy is not attacker for enemy in enemies):
            state += 1
        state += self.d20_disadvantage_state(attacker, attack=True)
        if self.has_status(attacker, "prone"):
            state -= 1
        if self.has_status(attacker, "invisible"):
            state += 1
        if self.has_status(target, "blinded"):
            state += 1
        if self.has_status(target, "restrained") or self.has_status(target, "stunned") or self.has_status(target, "paralyzed"):
            state += 1
        if self.has_status(target, "invisible") and "blind_sense" not in getattr(attacker, "features", []):
            state -= 1
        if self.has_status(target, "prone"):
            state += -1 if ranged else 1
        if self.has_status(target, "petrified") or self.has_status(target, "unconscious"):
            state += 1
        return 1 if state > 0 else -1 if state < 0 else 0

    def can_sneak_attack(self, attacker, heroes, target) -> bool:
        return any(hero.is_conscious() and hero is not attacker for hero in heroes) and target.is_conscious()

    def apply_poison_on_hit(self, attacker, target) -> None:
        dc = 12
        damage_roll = "1d4"
        condition_duration = 2
        always_damage = False
        source_text = f"{attacker.name}'s strike"
        if attacker.archetype == "mireweb_spider":
            dc = 11
            condition_duration = 1
            always_damage = True
            source_text = f"{attacker.name}'s venom"
        elif attacker.archetype == "ettervine_webherd":
            dc = 12
            condition_duration = 2
            always_damage = True
            source_text = f"{attacker.name}'s hooked fangs"
        elif attacker.archetype == "duskmire_matriarch":
            dc = 15
            damage_roll = "1d6"
            condition_duration = 2
            source_text = f"{attacker.name}'s widow venom"
        was_poisoned = self.has_status(target, "poisoned")
        save_success = self.saving_throw(target, "CON", dc, context=f"against {attacker.name}'s poisoned strike", against_poison=True)
        if save_success and not always_damage:
            return
        actual = self.apply_damage(
            target,
            self.roll_with_animation_context(
                damage_roll,
                style="damage",
                context_label=f"{attacker.name} poison damage",
                outcome_kind="damage",
            ).total,
            damage_type="poison",
        )
        self.say(f"{self.style_name(target)} suffers {self.style_damage(actual)} poison damage.")
        if not save_success:
            self.apply_status(target, "poisoned", condition_duration, source=source_text)
        if attacker.archetype == "rukhar" and not save_success and not self.saving_throw(target, "CON", 12, context=f"against {attacker.name}'s numbing poison", against_poison=True):
            self.apply_status(target, "paralyzed", 1, source=f"{attacker.name}'s numbing poison")
        if attacker.archetype == "varyn" and not save_success and not self.saving_throw(target, "CON", 12, context=f"against {attacker.name}'s draining toxin", against_poison=True):
            self.apply_status(target, "exhaustion", 2, source=f"{attacker.name}'s draining toxin")
        if attacker.archetype == "duskmire_matriarch" and not save_success and was_poisoned:
            if not self.saving_throw(target, "CON", 15, context=f"against {attacker.name}'s follow-up venom", against_poison=True):
                self.apply_status(target, "paralyzed", 1, source=f"{attacker.name}'s widow venom")
        self.announce_downed_target(target)

    def apply_damage(
        self,
        target,
        amount: int,
        *,
        damage_type: str = "",
        source_actor=None,
        apply_defense: bool = False,
        armor_break_percent: int = 0,
        armor_break: int = 0,
    ) -> int:
        self._last_damage_resolution = DamageResolution(raw_damage=max(0, amount))
        if target.dead:
            return 0
        if self.god_mode_enabled() and self.is_party_member_actor(target):
            return 0
        previous_hp = target.current_hp
        if (
            source_actor is not None
            and self.instant_kill_enabled()
            and self.is_party_member_actor(source_actor)
            and "enemy" in getattr(target, "tags", [])
        ):
            damage = 1000
            target.temp_hp = 0
            target.current_hp = 0
            target.dead = True
            self._last_damage_resolution = DamageResolution(
                raw_damage=max(0, amount),
                resisted_damage=damage,
                mitigated_damage=damage,
                hp_damage=damage,
                wound=damage > 0,
            )
            if previous_hp > 0:
                self.animate_health_bar_loss(target, previous_hp, target.current_hp)
                damage_hook = getattr(self, "after_actor_damaged", None)
                if callable(damage_hook):
                    damage_hook(target, previous_hp=previous_hp, damage=damage, damage_type=damage_type)
            return damage
        damage = max(0, amount)
        raw_damage = damage
        if self.has_status(target, "petrified"):
            damage //= 2
        resisted = False
        if damage_type == "poison" and "dwarven_resilience" in target.features:
            resisted = True
        if damage_type == "fire" and "hellish_resistance" in target.features:
            resisted = True
        if self.has_damage_resistance(target, damage_type):
            resisted = True
        if resisted:
            damage //= 2
        resisted_damage = damage
        defense_percent = 0
        total_armor_break_percent = 0
        if apply_defense and self.damage_type_uses_defense(damage_type):
            total_armor_break_percent = self.total_armor_break_percent(
                target,
                source_actor=source_actor,
                incoming_percent=armor_break_percent,
                incoming_steps=armor_break,
            )
            defense_percent = self.effective_defense_percent(
                target,
                damage_type=damage_type,
                armor_break_percent=total_armor_break_percent,
            )
            damage = damage * (100 - defense_percent) // 100
        mitigated_damage = damage
        ward_absorbed = self.absorb_ward_damage(target, damage, source_actor=source_actor, damage_type=damage_type)
        damage -= ward_absorbed
        temp_hp_absorbed = 0
        if target.temp_hp > 0:
            absorbed = min(target.temp_hp, damage)
            target.temp_hp -= absorbed
            damage -= absorbed
            temp_hp_absorbed = absorbed
        self._last_damage_resolution = DamageResolution(
            raw_damage=raw_damage,
            resisted_damage=resisted_damage,
            defense_percent=defense_percent,
            armor_break_percent=total_armor_break_percent,
            mitigated_damage=mitigated_damage,
            ward_absorbed=ward_absorbed,
            temp_hp_absorbed=temp_hp_absorbed,
            hp_damage=max(0, damage),
            glance=apply_defense and raw_damage > 0 and resisted_damage > 0 and mitigated_damage <= 0,
            wound=damage > 0,
        )
        self.trigger_damage_resolution_hooks(target, source_actor, damage_type=damage_type)
        if damage <= 0:
            return 0
        if target.current_hp == 0 and "enemy" not in target.tags:
            target.death_failures += 1
            if target.death_failures >= 3:
                target.dead = True
                if self.is_player_actor(target):
                    self.clear_liars_blessing_on_player_death()
            return damage
        target.current_hp = max(0, target.current_hp - damage)
        if target.current_hp == 0:
            if "enemy" in target.tags:
                if target.archetype == "cinderflame_skull" and target.resources.get("rekindle", 0) > 0:
                    target.resources["rekindle"] = 0
                    target.current_hp = 10
                    target.dead = False
                    self.say(f"{self.style_name(target)} collapses into ash, then flares back together with 10 hit points.")
                    return damage
                if target.archetype == "oathbroken_revenant" and target.resources.get("relentless_return", 0) > 0:
                    if str(target.bond_flags.get("marked_target", "")).strip():
                        target.resources["relentless_return"] = 0
                        target.current_hp = 12
                        target.dead = False
                        self.say(f"{self.style_name(target)} drags itself back upright on unfinished hatred with 12 hit points.")
                        return damage
                target.dead = True
            else:
                target.stable = False
                target.death_successes = 0
                target.death_failures = 0
        if target.current_hp < previous_hp:
            self.animate_health_bar_loss(target, previous_hp, target.current_hp)
            damage_hook = getattr(self, "after_actor_damaged", None)
            if callable(damage_hook):
                damage_hook(target, previous_hp=previous_hp, damage=damage, damage_type=damage_type)
        return damage

    def announce_downed_target(self, target) -> None:
        if target.current_hp == 0 and not target.dead and "enemy" not in target.tags:
            self.say(f"{self.style_name(target)} falls unconscious and begins making death resist checks.")

    def recover_after_battle(self) -> None:
        assert self.state is not None
        recovered: list[str] = []
        for member in self.state.party_members():
            if member.dead:
                continue
            if member.current_hp == 0:
                member.current_hp = 1
                member.stable = False
                member.death_successes = 0
                member.death_failures = 0
                recovered.append(member.name)
        if recovered:
            self.say("Once the danger passes, the party drags " + ", ".join(recovered) + " back to consciousness at 1 hit point.")

    def resolve_death_save(self, actor) -> None:
        d20 = self.roll_check_d20(
            actor,
            0,
            target_number=10,
            target_label="DC 10",
            modifier=0,
            style="save",
            outcome_kind="save",
            context_label=f"{actor.name} death resist",
        )
        if d20.kept == 1:
            actor.death_failures += 2
            self.say(f"{self.style_name(actor)} rolls a natural 1 on a death resist check and suffers two failures.")
        elif d20.kept == 20:
            actor.current_hp = 1
            actor.death_successes = 0
            actor.death_failures = 0
            self.say(f"{self.style_name(actor)} rolls a natural 20 and staggers back to {self.style_healing(1)} hit point.")
            return
        elif d20.kept >= 10:
            actor.death_successes += 1
            self.say(f"{self.style_name(actor)} succeeds on a death resist check.")
        else:
            actor.death_failures += 1
            self.say(f"{self.style_name(actor)} fails a death resist check.")
        if actor.death_successes >= 3:
            actor.stable = True
            actor.death_successes = 0
            actor.death_failures = 0
            self.say(f"{self.style_name(actor)} stabilizes at 0 hit points.")
        if actor.death_failures >= 3:
            actor.dead = True
            if self.is_player_actor(actor):
                self.clear_liars_blessing_on_player_death()

    def skill_check(self, actor, skill: str, dc: int, *, context: str) -> bool:
        commit_pending_story_check_choice_attempt = getattr(self, "commit_pending_story_check_choice_attempt", None)
        if callable(commit_pending_story_check_choice_attempt):
            commit_pending_story_check_choice_attempt()
        dc = self.effective_skill_dc(dc, context=context)
        if self.always_fail_dice_checks_enabled() and self.is_party_member_actor(actor):
            self.set_pending_scaled_check_reward(False)
            self.say(f"{self.style_name(actor)} automatically fails the {self.style_skill_label(skill)} check {context}.")
            self.say("")
            return False
        advantage = self.d20_disadvantage_state(actor, skill=skill, context=context)
        companion_modifier = 0
        companion_lines: list[str] = []
        companion_assist = getattr(self, "companion_skill_check_assist", None)
        if callable(companion_assist):
            companion_modifier, companion_lines = companion_assist(actor, skill, context)
        for line in companion_lines:
            self.say(line)
        total_modifier = actor.skill_bonus(skill) + companion_modifier
        d20 = self.roll_check_d20(
            actor,
            advantage,
            target_number=dc,
            target_label=f"DC {dc}",
            modifier=total_modifier,
            style="skill",
            outcome_kind="check",
            context_label=f"{actor.name} {skill} check",
        )
        total = d20.kept + total_modifier
        self.say(
            f"{self.style_name(actor)} makes a {self.style_skill_label(skill)} check {context}: {total} vs DC {dc}."
        )
        success = total >= dc
        play_sound_effect = getattr(self, "play_sound_effect", None)
        if callable(play_sound_effect):
            play_sound_effect("skill_success" if success else "skill_fail")
        self.set_pending_scaled_check_reward(success and self.is_party_member_actor(actor))
        if not success:
            self.say("")
        return success

    def saving_throw(self, actor, ability: str, dc: int, *, context: str, against_poison: bool = False) -> bool:
        resist_label = f"{ability_label(ability, include_code=True)} resist"
        if self.always_fail_dice_checks_enabled() and self.is_party_member_actor(actor):
            self.say(f"{self.style_name(actor)} automatically fails the {resist_label} {context}.")
            return False
        if self.always_pass_dice_checks_enabled() and self.is_party_member_actor(actor):
            self.say(f"{self.style_name(actor)} automatically clears the {resist_label} {context}.")
            return True
        if self.auto_fail_save(actor, ability):
            self.say(f"{self.style_name(actor)} automatically fails the {resist_label} {context}.")
            return False
        advantage = 1 if against_poison and "dwarven_resilience" in actor.features else 0
        if ability == "DEX" and self.actor_is_dodging(actor):
            advantage += 1
        if self.has_status(actor, "restrained") and ability == "DEX":
            advantage -= 1
        exhaustion = max(0, int(actor.conditions.get("exhaustion", 0)))
        if exhaustion >= 3:
            advantage -= 1
        total_modifier = (
            actor.save_bonus(ability)
            + self.status_value(actor, "save_bonus")
            - self.status_value(actor, "save_penalty")
        )
        d20 = self.roll_check_d20(
            actor,
            advantage,
            target_number=dc,
            target_label=f"DC {dc}",
            modifier=total_modifier,
            style="save",
            outcome_kind="save",
            context_label=f"{actor.name} {resist_label}",
        )
        total = d20.kept + total_modifier
        self.say(f"{self.style_name(actor)} makes a {resist_label} {context}: {total} vs DC {dc}.")
        return total >= dc

    def roll_with_advantage(self, actor, advantage_state: int) -> D20Outcome:
        return roll_d20(self.rng, advantage_state=advantage_state, lucky="lucky" in actor.features)

    def roll_check_d20(
        self,
        actor,
        advantage_state: int,
        *,
        target_number: int | None = None,
        target_label: str | None = None,
        modifier: int = 0,
        context_label: str | None = None,
        style: str | None = None,
        outcome_kind: str | None = None,
    ) -> D20Outcome:
        if self.always_fail_dice_checks_enabled() and self.is_party_member_actor(actor):
            forced_rolls = [1, 1] if advantage_state != 0 else [1]
            return D20Outcome(kept=1, rolls=forced_rolls, rerolls=[], advantage_state=advantage_state)
        if self.always_pass_dice_checks_enabled() and self.is_party_member_actor(actor):
            kept = 20
            if target_number is not None:
                kept = max(2, target_number - modifier)
            forced_rolls = [kept, kept] if advantage_state != 0 else [kept]
            return D20Outcome(kept=kept, rolls=forced_rolls, rerolls=[], advantage_state=advantage_state)
        with self.temporary_roll_animation_metadata(
            target_number=target_number,
            target_label=target_label,
            total_modifier=modifier,
            context_label=context_label,
            style=style,
            outcome_kind=outcome_kind,
        ):
            return self.roll_with_advantage(actor, advantage_state)

    def roll_initiative(self, heroes, enemies, *, hero_bonus: int = 0, enemy_bonus: int = 0) -> list:
        entries: list[dict[str, object]] = []
        with self.suspend_dice_roll_animation():
            for index, actor in enumerate(heroes):
                if actor.dead:
                    continue
                modifier = actor.ability_mod("DEX") + hero_bonus + self.initiative_bonus(actor)
                outcome = self.roll_check_d20(
                    actor,
                    0,
                    modifier=modifier,
                    context_label=f"{actor.name} rolls initiative",
                    style="initiative",
                    outcome_kind="initiative",
                )
                entries.append(
                    {
                        "actor": actor,
                        "outcome": outcome,
                        "modifier": modifier,
                        "total": outcome.kept + modifier,
                        "dex_mod": actor.ability_mod("DEX"),
                        "side_priority": 1,
                        "tie_index": -index,
                    }
                )
            for index, actor in enumerate(enemies):
                modifier = actor.ability_mod("DEX") + enemy_bonus + self.initiative_bonus(actor)
                outcome = self.roll_check_d20(
                    actor,
                    0,
                    modifier=modifier,
                    context_label=f"{actor.name} rolls initiative",
                    style="initiative",
                    outcome_kind="initiative",
                )
                entries.append(
                    {
                        "actor": actor,
                        "outcome": outcome,
                        "modifier": modifier,
                        "total": outcome.kept + modifier,
                        "dex_mod": actor.ability_mod("DEX"),
                        "side_priority": 0,
                        "tie_index": -index,
                    }
                )
        entries.sort(
            key=lambda entry: (entry["total"], entry["dex_mod"], entry["side_priority"], entry["tie_index"]),
            reverse=True,
        )
        self.animate_initiative_rolls(entries)
        return [entry["actor"] for entry in entries]

    def describe_living_combatants(self, combatants) -> list[str]:
        living = [combatant for combatant in combatants if not combatant.dead]
        name_width = max((len(strip_ansi(self.style_name(combatant))) for combatant in living), default=0)
        return [self.describe_combatant(combatant, name_width=name_width) for combatant in living]

    def combat_roster_panel(self, title: str, color: str, lines: list[str], *, empty_message: str):
        return Panel(
            Group(*(self.rich_from_ansi(line) for line in (lines or [empty_message]))),
            title=self.rich_text(title, color, bold=True),
            border_style=rich_style_name(color),
            box=box.ROUNDED,
            padding=(0, 1),
        )

    def combat_battlefield_row_renderable(self, hero_lines: list[str], enemy_lines: list[str]):
        if not self.rich_enabled() or Panel is None or Group is None or box is None:
            return None
        party_panel = self.combat_roster_panel(
            "Party",
            "light_aqua",
            hero_lines,
            empty_message="No one is still standing.",
        )
        enemy_panel = self.combat_roster_panel(
            "Enemies",
            "light_red",
            enemy_lines,
            empty_message="Enemies routed.",
        )
        return self.rich_panel_row_renderable([party_panel, enemy_panel], ratios=[1, 1], padding=(0, 1))

    def print_battlefield(self, heroes, enemies) -> None:
        hero_lines = self.describe_living_combatants(heroes)
        enemy_lines = self.describe_living_combatants(enemies)
        battlefield_row = self.combat_battlefield_row_renderable(hero_lines, enemy_lines)
        if battlefield_row is not None and self.emit_rich(battlefield_row, width=self.safe_rich_render_width()):
            return
        if any("\n" in line for line in (*hero_lines, *enemy_lines)):
            self.say("Party:")
            for line in hero_lines:
                self.say(line)
            self.say("Enemies:")
            for line in enemy_lines:
                self.say(line)
            return
        self.say("Party: " + " | ".join(hero_lines))
        self.say("Enemies: " + " | ".join(enemy_lines))

    def describe_combatant(self, creature, *, name_width: int | None = None) -> str:
        active_conditions = [self.status_name(name) for name, value in creature.conditions.items() if value != 0]
        conditions = f" ({', '.join(active_conditions)})" if active_conditions else ""
        temp = f", temp {creature.temp_hp}" if creature.temp_hp else ""
        name = self.style_name(creature)
        plain_name = strip_ansi(name)
        if name_width is None:
            prefix = f"{name}: "
            indent_width = len(plain_name) + 2
        else:
            prefix = f"{name}:{' ' * (max(0, name_width - len(plain_name)) + 1)}"
            indent_width = name_width + 2
        if creature.dead:
            return f"{prefix}{self.format_health_bar(0, creature.max_hp)} (dead){conditions}"
        if creature.current_hp == 0 and not creature.dead:
            return f"{prefix}{self.format_health_bar(0, creature.max_hp)} (down){conditions}"
        line = (
            f"{prefix}{self.format_health_bar(creature.current_hp, creature.max_hp)}, "
            f"{self.combat_defense_summary(creature)}{temp}{conditions}"
        )
        resource_lines = [
            line
            for line in (
                self.format_member_magic_bar(creature),
                self.combat_resource_summary_line(creature),
            )
            if line is not None
        ]
        if not resource_lines:
            return line
        indent = " " * indent_width
        return f"{line}\n" + "\n".join(f"{indent}{resource_line}" for resource_line in resource_lines)

    def handle_defeat(self, reason: str) -> None:
        play_sound_effect = getattr(self, "play_sound_effect", None)
        if callable(play_sound_effect):
            play_sound_effect("game_over")
        self.banner("Defeat")
        self.say(reason)
        choice = self.choose(
            "What do you want to do?",
            [
                "Return to the title screen",
                "Open Save Files",
            ],
            allow_meta=False,
        )
        if choice == 2:
            loaded = self.open_save_files_menu()
            if loaded:
                return
        self.state = None
