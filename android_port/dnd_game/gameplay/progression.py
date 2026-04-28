from __future__ import annotations

import math

from ..content import CLASS_LEVEL_PROGRESSION, CLASSES
from ..data.story.companions import companion_default_subclass
from ..data.story.public_terms import class_label, feature_label, marks_label, rules_text, skill_option_label
from .class_framework import synchronize_class_resources
from .magic_points import synchronize_magic_points
from .spell_slots import synchronize_spell_slots
from ..models import Character
from .constants import LEVEL_XP_THRESHOLDS

COMPANION_SUBCLASS_LEVEL = 3
COMPANION_SUBCLASS_KEY = "companion_subclass"
COMPANION_SUBCLASS_ELIGIBLE_KEY = "companion_subclass_player_choice_eligible"
COMPANION_SUBCLASS_RECRUITED_LEVEL_KEY = "companion_recruited_level"
COMPANION_SUBCLASS_PREPICKED_KEY = "companion_subclass_prepicked"
COMPANION_SUBCLASS_PLAYER_CHOSEN_KEY = "companion_subclass_player_chosen"
PLAYER_LEVEL_UP_SKILL_PICKS_KEY = "player_level_up_skill_picks_pending"

CLASS_SUBCLASS_OPTIONS: dict[str, tuple[dict[str, str], ...]] = {
    "Warrior": (
        {
            "id": "juggernaut",
            "label": "Juggernaut",
            "description": "Guard, Glance, Momentum, and hard lane control.",
        },
        {
            "id": "weapon_master",
            "label": "Weapon Master",
            "description": "Armor Break, style switching, and anti-Guard pressure.",
        },
        {
            "id": "berserker",
            "label": "Berserker",
            "description": "Risk-heavy damage, Fury, and wound-window pressure.",
        },
        {
            "id": "bloodreaver",
            "label": "Bloodreaver",
            "description": "Blood Debt, marks, cost-paid healing, and sustain.",
        },
    ),
    "Rogue": (
        {
            "id": "shadowguard",
            "label": "Shadowguard",
            "description": "Avoidance tanking, decoys, smoke pins, and lane cover.",
        },
        {
            "id": "assassin",
            "label": "Assassin",
            "description": "Opener burst, Death Mark, exposed targets, and finishing cuts.",
        },
        {
            "id": "poisoner",
            "label": "Poisoner",
            "description": "Toxin pressure, condition damage, and armor workarounds.",
        },
        {
            "id": "alchemist",
            "label": "Alchemist",
            "description": "Satchel healing, smoke, acid, and field utility.",
        },
    ),
    "Mage": (
        {
            "id": "spellguard",
            "label": "Spellguard",
            "description": "Ward, shells, defensive hooks, and lockstep fields.",
        },
        {
            "id": "arcanist",
            "label": "Arcanist",
            "description": "Pattern Charge, Arc setup, force pulses, and detonation.",
        },
        {
            "id": "elementalist",
            "label": "Elementalist",
            "description": "Attunement, fields, terrain pressure, and area saves.",
        },
        {
            "id": "aethermancer",
            "label": "Aethermancer",
            "description": "Flow, healing, condition repair, and overflow Ward.",
        },
    ),
}

CLASS_SUBCLASS_FEATURE_IDS: dict[str, dict[int, dict[str, list[str]]]] = {
    "Warrior": {
        3: {
            "juggernaut": ["juggernaut_momentum", "iron_draw", "shoulder_in", "line_holder"],
            "weapon_master": ["weapon_master_combo", "style_wheel", "measure_twice"],
            "berserker": ["berserker_fury", "redline", "reckless_cut"],
            "bloodreaver": ["bloodreaver_blood_debt", "red_mark", "blood_price"],
        },
        4: {
            "juggernaut": [],
            "weapon_master": ["clean_line", "dent_the_shell", "hook_the_guard"],
            "berserker": ["teeth_set", "drink_the_hurt"],
            "bloodreaver": ["war_salve_strike", "open_the_ledger"],
        },
    },
    "Rogue": {
        3: {
            "shadowguard": ["shadowguard_shadow"],
            "assassin": ["death_mark"],
            "poisoner": ["poisoner_toxin"],
            "alchemist": ["alchemist_quick_mix"],
        },
        4: {
            "shadowguard": ["false_target", "smoke_pin", "cover_the_healer"],
            "assassin": ["quiet_knife", "between_plates", "sudden_end"],
            "poisoner": ["black_drop", "green_needle", "bitter_cloud", "rot_thread", "bloom_in_the_blood"],
            "alchemist": ["redcap_tonic", "smoke_jar", "bitter_acid", "field_stitch"],
        },
    },
    "Mage": {
        3: {
            "spellguard": ["spellguard_ward"],
            "arcanist": ["arcanist_arc"],
            "elementalist": ["elementalist_attunement"],
            "aethermancer": ["aethermancer_flow"],
        },
        4: {
            "spellguard": ["anchor_shell", "ward_shell", "blue_glass_palm", "lockstep_field"],
            "arcanist": ["pattern_charge", "arc_pulse", "marked_angle", "quiet_sum", "detonate_pattern"],
            "elementalist": [
                "elemental_weave",
                "ember_lance",
                "frost_shard",
                "volt_grasp",
                "change_weather_hand",
                "burning_line",
                "lockfrost",
            ],
            "aethermancer": [
                "field_mend",
                "pulse_restore",
                "triage_line",
                "clean_breath",
                "steady_pulse",
                "overflow_shell",
            ],
        },
    },
}

CLASS_SUBCLASS_FEATURE_ID_SETS: dict[str, set[str]] = {
    class_name: {
        feature_id
        for levels in level_map.values()
        for features_by_subclass in levels.values()
        for feature_id in features_by_subclass
    }
    for class_name, level_map in CLASS_SUBCLASS_FEATURE_IDS.items()
}


class ProgressionMixin:
    def level_up_skill_choices_for(self, actor: Character) -> list[str]:
        return [skill for skill in CLASSES[actor.class_name]["skill_choices"] if skill not in actor.skill_proficiencies]

    def pending_player_level_up_skill_levels(self) -> list[int]:
        if self.state is None:
            return []
        raw_levels = self.state.flags.get(PLAYER_LEVEL_UP_SKILL_PICKS_KEY, [])
        if isinstance(raw_levels, int):
            raw_items = [raw_levels]
        elif isinstance(raw_levels, (list, tuple)):
            raw_items = list(raw_levels)
        else:
            raw_items = []
        levels: list[int] = []
        for raw_level in raw_items:
            try:
                level = int(raw_level)
            except (TypeError, ValueError):
                continue
            if level >= 2:
                levels.append(level)
        if raw_levels != levels:
            if levels:
                self.state.flags[PLAYER_LEVEL_UP_SKILL_PICKS_KEY] = levels
            else:
                self.state.flags.pop(PLAYER_LEVEL_UP_SKILL_PICKS_KEY, None)
        return levels

    def set_pending_player_level_up_skill_levels(self, levels: list[int]) -> None:
        if self.state is None:
            return
        clean_levels: list[int] = []
        for raw_level in levels:
            try:
                level = int(raw_level)
            except (TypeError, ValueError):
                continue
            if level >= 2:
                clean_levels.append(level)
        clean_levels.sort()
        if clean_levels:
            self.state.flags[PLAYER_LEVEL_UP_SKILL_PICKS_KEY] = clean_levels
        else:
            self.state.flags.pop(PLAYER_LEVEL_UP_SKILL_PICKS_KEY, None)

    def add_pending_player_level_up_skill_pick(self, level: int) -> None:
        if self.state is None:
            return
        pending_levels = self.pending_player_level_up_skill_levels()
        pending_levels.append(int(level))
        self.set_pending_player_level_up_skill_levels(pending_levels)

    def has_pending_player_level_up_choices(self) -> bool:
        if self.state is None:
            return False
        pending_levels = self.pending_player_level_up_skill_levels()
        if not pending_levels:
            return False
        if not self.level_up_skill_choices_for(self.state.player):
            self.set_pending_player_level_up_skill_levels([])
            return False
        return True

    def level_up_reminder_text(self) -> str:
        if not self.has_pending_player_level_up_choices():
            return ""
        pending_levels = self.pending_player_level_up_skill_levels()
        level_text = ", ".join(f"level {level}" for level in pending_levels)
        if len(pending_levels) == 1:
            return f"The party leveled up to {level_text}. Type `level` to choose a new class skill."
        return f"The party leveled up through {level_text}. Type `level` to choose new class skills."

    def complete_one_pending_player_level_up_skill_pick(self) -> None:
        pending_levels = self.pending_player_level_up_skill_levels()
        if pending_levels:
            pending_levels.pop(0)
        self.set_pending_player_level_up_skill_levels(pending_levels)

    def class_progression_summary_lines(self, actor: Character) -> list[tuple[int, str, str]]:
        progression_by_level = CLASS_LEVEL_PROGRESSION.get(actor.class_name, {})
        lines: list[tuple[int, str, str]] = []
        for level in sorted(progression_by_level):
            progression = progression_by_level[level]
            feature_ids = list(progression.get("feature_ids", []))
            labels = [feature_label(feature_id) for feature_id in feature_ids]
            state = "unlocked" if level <= actor.level else "later"
            lines.append((level, state, ", ".join(labels) if labels else "No listed feature"))
        return lines

    def subclass_progression_summary_lines(self, actor: Character) -> list[tuple[str, str]]:
        options = CLASS_SUBCLASS_OPTIONS.get(actor.class_name, ())
        return [(str(option["label"]), str(option["description"])) for option in options]

    def build_level_up_renderable(self, actor: Character, available: list[str], pending_levels: list[int]):
        from ..ui.rich_render import Group, Panel, Table, Text, box
        from ..ui.colors import rich_style_name

        if Group is None or Panel is None or Table is None or Text is None or box is None:
            return None

        pending_text = ", ".join(f"level {level}" for level in pending_levels)
        header = Text()
        header.append(f"{actor.name} reached {pending_text}.\n", style=f"bold {rich_style_name('light_yellow')}")
        header.append("Choose one new class skill for each waiting level.", style="dim")

        progression_table = Table(box=box.SIMPLE_HEAVY, expand=True, pad_edge=False)
        progression_table.add_column("Level", style=f"bold {rich_style_name('light_yellow')}", width=8)
        progression_table.add_column("State", width=10)
        progression_table.add_column("Class Progression", ratio=1)
        for level, state, features in self.class_progression_summary_lines(actor):
            state_style = rich_style_name("light_green") if state == "unlocked" else "dim"
            progression_table.add_row(f"{level}", Text(state.title(), style=state_style), features)

        subclass_table = Table(box=box.SIMPLE_HEAVY, expand=True, pad_edge=False)
        subclass_table.add_column("Subclass Path", style=f"bold {rich_style_name('light_aqua')}", width=18)
        subclass_table.add_column("Focus", ratio=1)
        for label, description in self.subclass_progression_summary_lines(actor):
            subclass_table.add_row(label, description)

        skill_table = Table(box=box.SIMPLE_HEAVY, expand=True, pad_edge=False)
        skill_table.add_column("#", style=f"bold {rich_style_name('light_yellow')}", width=4)
        skill_table.add_column("Available Skill", ratio=1)
        for index, skill in enumerate(available, start=1):
            skill_table.add_row(f"{index}.", skill_option_label(skill))

        footer = Text()
        footer.append("Type a number to learn that skill. Type ", style="dim")
        footer.append("back", style=f"bold {rich_style_name('light_yellow')} dim")
        footer.append(" to return.", style="dim")

        return Panel(
            Group(
                header,
                self.rich_text("", dim=True),
                progression_table,
                self.rich_text("", dim=True),
                subclass_table,
                self.rich_text("", dim=True),
                skill_table,
                self.rich_text("", dim=True),
                footer,
            ),
            title=self.rich_text("Level Up", "light_yellow", bold=True),
            border_style=rich_style_name("light_yellow"),
            box=box.ROUNDED,
            padding=(0, 1),
        )

    def render_level_up_ui(self, actor: Character, available: list[str], pending_levels: list[int]) -> None:
        renderable = self.build_level_up_renderable(actor, available, pending_levels)
        if renderable is not None and self.should_use_rich_ui() and self.emit_rich(renderable, width=self.safe_rich_render_width()):
            return
        self.banner("Level Up")
        self.say(self.level_up_reminder_text() or f"{actor.name} has level-up training waiting.")
        self.output_fn("Class Progression:")
        for level, state, features in self.class_progression_summary_lines(actor):
            self.output_fn(f"  Level {level} [{state}]: {features}")
        subclass_lines = self.subclass_progression_summary_lines(actor)
        if subclass_lines:
            self.output_fn("")
            self.output_fn("Subclass Paths:")
            for label, description in subclass_lines:
                self.output_fn(f"  {label}: {description}")
        self.output_fn("")
        self.output_fn("Available Skills:")
        for index, skill in enumerate(available, start=1):
            self.output_fn(f"  {index}. {skill_option_label(skill)}")
        self.output_fn("Type a number to learn that skill, or back.")

    def choose_pending_level_up_skill(self, actor: Character) -> bool:
        pending_levels = self.pending_player_level_up_skill_levels()
        available = self.level_up_skill_choices_for(actor)
        if not pending_levels:
            self.say("No level-up training is waiting.")
            return False
        if not available:
            self.say(f"{actor.name} has no new {class_label(actor.class_name)} skills available to learn.")
            self.set_pending_player_level_up_skill_levels([])
            return False

        while True:
            raw = self.read_resize_aware_input(
                lambda: self.render_level_up_ui(actor, available, pending_levels),
                prompt="level> ",
            ).strip()
            lowered = raw.lower()
            if lowered in {"", "back", "exit", "quit"}:
                self.say("Level-up training remains available. Type `level` when you are ready.")
                return False
            if lowered == "level":
                self.say("You are already choosing level-up training.")
                continue
            if raw.isdigit():
                choice = int(raw)
                if 1 <= choice <= len(available):
                    picked = available[choice - 1]
                    actor.skill_proficiencies.append(picked)
                    actor.skill_proficiencies.sort()
                    self.complete_one_pending_player_level_up_skill_pick()
                    self.say(f"{actor.name} learns {skill_option_label(picked)}.")
                    return True
            self.say("Please enter a listed number, or type back.")

    def open_level_up_menu(self) -> bool:
        if self.state is None:
            self.say("There is no active party to train yet.")
            return False
        completed = False
        while self.pending_player_level_up_skill_levels():
            if not self.level_up_skill_choices_for(self.state.player):
                self.say(f"{self.state.player.name} has no new {class_label(self.state.player.class_name)} skills available to learn.")
                self.set_pending_player_level_up_skill_levels([])
                break
            if not self.choose_pending_level_up_skill(self.state.player):
                break
            completed = True
        if completed and not self.pending_player_level_up_skill_levels():
            self.say("Level-up training is complete.")
        elif not completed and not self.has_pending_player_level_up_choices():
            self.say("No level-up training is waiting.")
        return completed

    def handle_meta_command(self, raw: str) -> bool:
        if raw.strip().lower() == "level":
            self.open_level_up_menu()
            return True
        return super().handle_meta_command(raw)

    def companion_subclass_options(self, actor: Character) -> tuple[dict[str, str], ...]:
        if not getattr(actor, "companion_id", ""):
            return ()
        return CLASS_SUBCLASS_OPTIONS.get(actor.class_name, ())

    def companion_subclass_ids(self, actor: Character) -> set[str]:
        return {str(option["id"]) for option in self.companion_subclass_options(actor)}

    def companion_subclass_label(self, actor: Character, subclass_id: str) -> str:
        for option in self.companion_subclass_options(actor):
            if option["id"] == subclass_id:
                return option["label"]
        return subclass_id.replace("_", " ").title()

    def companion_default_subclass_for_actor(self, actor: Character) -> str | None:
        valid_ids = self.companion_subclass_ids(actor)
        if not valid_ids:
            return None
        default_id = str(
            getattr(actor, "bond_flags", {}).get("default_subclass")
            or companion_default_subclass(getattr(actor, "companion_id", ""))
        )
        if default_id in valid_ids:
            return default_id
        return str(self.companion_subclass_options(actor)[0]["id"])

    def mark_companion_subclass_recruitment(self, companion: Character) -> None:
        if not self.companion_subclass_options(companion):
            return
        flags = companion.bond_flags
        recruited_level = int(flags.get(COMPANION_SUBCLASS_RECRUITED_LEVEL_KEY, companion.level))
        flags[COMPANION_SUBCLASS_RECRUITED_LEVEL_KEY] = recruited_level
        if recruited_level <= 2 and COMPANION_SUBCLASS_KEY not in flags:
            flags[COMPANION_SUBCLASS_ELIGIBLE_KEY] = True
            return
        flags[COMPANION_SUBCLASS_ELIGIBLE_KEY] = False
        self.ensure_companion_subclass(companion, allow_choice=False, announce=True)

    def choose_companion_subclass(self, actor: Character) -> str:
        options = list(self.companion_subclass_options(actor))
        choice = self.choose(
            f"Choose {actor.name}'s {class_label(actor.class_name)} subclass.",
            [f"{option['label']}: {option['description']}" for option in options],
            allow_meta=False,
        )
        return str(options[choice - 1]["id"])

    def ensure_companion_subclass(self, actor: Character, *, allow_choice: bool, announce: bool) -> str | None:
        if actor.level < COMPANION_SUBCLASS_LEVEL:
            return None
        valid_ids = self.companion_subclass_ids(actor)
        if not valid_ids:
            return None
        flags = actor.bond_flags
        existing = str(flags.get(COMPANION_SUBCLASS_KEY, ""))
        if existing in valid_ids:
            return existing
        default_id = self.companion_default_subclass_for_actor(actor)
        if default_id is None:
            return None
        recruited_level = flags.get(COMPANION_SUBCLASS_RECRUITED_LEVEL_KEY)
        inferred_early_recruit = recruited_level is None and actor.level == COMPANION_SUBCLASS_LEVEL
        eligible = bool(flags.get(COMPANION_SUBCLASS_ELIGIBLE_KEY)) or inferred_early_recruit
        if allow_choice and eligible:
            subclass_id = self.choose_companion_subclass(actor)
            flags[COMPANION_SUBCLASS_PLAYER_CHOSEN_KEY] = True
            flags[COMPANION_SUBCLASS_PREPICKED_KEY] = False
        else:
            subclass_id = default_id
            flags[COMPANION_SUBCLASS_PLAYER_CHOSEN_KEY] = False
            flags[COMPANION_SUBCLASS_PREPICKED_KEY] = True
        flags[COMPANION_SUBCLASS_KEY] = subclass_id
        flags["companion_subclass_label"] = self.companion_subclass_label(actor, subclass_id)
        if announce:
            self.say(f"{actor.name} commits to {self.companion_subclass_label(actor, subclass_id)} training.")
        return subclass_id

    def companion_subclass_feature_ids_for_level(
        self,
        actor: Character,
        level: int,
        base_feature_ids: list[str],
    ) -> list[str]:
        subclass_id = self.ensure_companion_subclass(actor, allow_choice=False, announce=False)
        if not subclass_id:
            return list(base_feature_ids)
        all_subclass_features = CLASS_SUBCLASS_FEATURE_ID_SETS.get(actor.class_name, set())
        selected_features = CLASS_SUBCLASS_FEATURE_IDS.get(actor.class_name, {}).get(level, {}).get(subclass_id, [])
        feature_ids = [feature_id for feature_id in base_feature_ids if feature_id not in all_subclass_features]
        for feature_id in selected_features:
            if feature_id not in feature_ids:
                feature_ids.append(feature_id)
        return feature_ids

    def prune_unselected_companion_subclass_features(self, actor: Character) -> None:
        subclass_id = str(getattr(actor, "bond_flags", {}).get(COMPANION_SUBCLASS_KEY, ""))
        if not subclass_id:
            return
        all_subclass_features = CLASS_SUBCLASS_FEATURE_ID_SETS.get(actor.class_name, set())
        if not all_subclass_features:
            return
        allowed_features: set[str] = set()
        for features_by_subclass in CLASS_SUBCLASS_FEATURE_IDS.get(actor.class_name, {}).values():
            allowed_features.update(features_by_subclass.get(subclass_id, []))
        actor.features = sorted(feature_id for feature_id in actor.features if feature_id not in all_subclass_features or feature_id in allowed_features)

    def feature_lines_for_ids(
        self,
        actor: Character,
        progression: dict[str, object],
        base_feature_ids: list[str],
        feature_ids: list[str],
    ) -> list[str]:
        described_features: dict[str, tuple[str, str]] = {}
        for index, pair in enumerate(progression.get("features", [])):
            if index >= len(base_feature_ids):
                continue
            title, description = pair
            described_features[base_feature_ids[index]] = (str(title), str(description))
        subclass_id = str(getattr(actor, "bond_flags", {}).get(COMPANION_SUBCLASS_KEY, ""))
        subclass_label = self.companion_subclass_label(actor, subclass_id) if subclass_id else ""
        feature_lines: list[str] = []
        for feature_id in feature_ids:
            if feature_id in described_features:
                _title, description = described_features[feature_id]
                feature_lines.append(f"{feature_label(feature_id)}: {rules_text(description)}")
            elif subclass_label:
                feature_lines.append(f"{feature_label(feature_id)}: {rules_text(f'Unlocked by {subclass_label} training.')}")
            else:
                feature_lines.append(f"{feature_label(feature_id)}.")
        return feature_lines

    def reconcile_level_progression(self, actor: Character) -> None:
        self.scale_level_resources(actor, refill=True)
        for level in range(2, actor.level + 1):
            self.apply_class_level_features(actor, level, announce=False)

    def current_level_target(self) -> int | None:
        if self.state is None:
            return None
        return LEVEL_XP_THRESHOLDS.get(self.state.player.level + 1)

    def current_level_floor(self) -> int:
        if self.state is None:
            return 0
        return LEVEL_XP_THRESHOLDS.get(self.state.player.level, 0)

    def max_xp_to_next_level(self) -> int | None:
        if self.state is None:
            return None
        target = self.current_level_target()
        if target is None:
            return None
        return max(0, target - self.current_level_floor())

    def xp_to_next_level(self) -> int | None:
        if self.state is None:
            return None
        target = self.current_level_target()
        if target is None:
            return None
        return max(0, target - self.state.xp)

    def xp_progress_summary(self) -> str:
        if self.state is None:
            return "No party XP yet."
        target = self.current_level_target()
        if target is None:
            return f"Party XP: {self.state.xp} (maximum implemented level reached)"
        return f"Party XP: {self.state.xp} | Next level in {max(0, target - self.state.xp)} XP"

    def scaled_check_reward_xp(self) -> int:
        if self.state is None:
            return 0
        per_level_floor = 20 * max(1, self.state.player.level)
        band_xp = self.max_xp_to_next_level()
        if band_xp is None:
            return per_level_floor
        return max(per_level_floor, math.ceil(band_xp * 0.025))

    def clear_pending_scaled_check_reward(self) -> None:
        self._pending_scaled_check_reward = False

    def set_pending_scaled_check_reward(self, enabled: bool) -> None:
        self._pending_scaled_check_reward = bool(enabled)

    def apply_class_level_features(self, actor: Character, level: int, *, announce: bool) -> list[str]:
        progression = CLASS_LEVEL_PROGRESSION.get(actor.class_name, {}).get(level)
        if progression is None:
            return []
        base_feature_ids = list(progression.get("feature_ids", []))
        feature_ids = self.companion_subclass_feature_ids_for_level(actor, level, base_feature_ids)
        self.prune_unselected_companion_subclass_features(actor)
        if feature_ids and all(feature_id in actor.features for feature_id in feature_ids):
            return []
        for feature_id in feature_ids:
            if feature_id not in actor.features:
                actor.features.append(feature_id)
        for resource_name, amount in dict(progression.get("resources", {})).items():
            actor.max_resources[resource_name] = max(actor.max_resources.get(resource_name, 0), amount)
            actor.resources[resource_name] = actor.max_resources[resource_name]
        for bonus_name, amount in dict(progression.get("equipment_bonuses", {})).items():
            actor.equipment_bonuses[bonus_name] = actor.equipment_bonuses.get(bonus_name, 0) + amount
        feature_lines = self.feature_lines_for_ids(actor, progression, base_feature_ids, feature_ids)
        if announce:
            for line in feature_lines:
                self.say(line)
        actor.features.sort()
        self.prune_unselected_companion_subclass_features(actor)
        synchronize_class_resources(actor, refill=True)
        return feature_lines

    def reward_party(self, *, xp: int = 0, gold: int = 0, reason: str) -> None:
        assert self.state is not None
        gained_parts: list[str] = []
        use_scaled_check_reward = bool(xp and getattr(self, "_pending_scaled_check_reward", False))
        if use_scaled_check_reward:
            xp = self.scaled_check_reward_xp()
        self.clear_pending_scaled_check_reward()
        if xp:
            self.state.xp += xp
            gained_parts.append(f"{xp} XP")
        if gold:
            self.state.gold += gold
            gained_parts.append(marks_label(gold))
        if gained_parts:
            self.say(f"Reward gained for {reason}: {', '.join(gained_parts)}.")
            self.say(self.xp_progress_summary())
            self.add_journal(f"Reward from {reason}: {', '.join(gained_parts)}.")
        self.resolve_level_ups()

    def resolve_level_ups(self) -> None:
        assert self.state is not None
        while self.state.player.level + 1 in LEVEL_XP_THRESHOLDS and self.state.xp >= LEVEL_XP_THRESHOLDS[self.state.player.level + 1]:
            new_level = self.state.player.level + 1
            self.banner(f"Level {new_level}")
            self.say(f"The party reaches level {new_level}. Training and hard road lessons start to pay off.")
            for member in [self.state.player, *self.state.all_companions()]:
                self.level_up_character(member, new_level)

    def level_up_character(self, actor: Character, new_level: int) -> None:
        actor.level = new_level
        hp_gain = max(1, actor.hit_die // 2 + 1 + actor.ability_mod("CON"))
        actor.max_hp += hp_gain
        actor.current_hp += hp_gain
        self.scale_level_resources(actor)
        self.ensure_companion_subclass(actor, allow_choice=True, announce=True)
        feature_lines = self.apply_class_level_features(actor, new_level, announce=False)
        if actor is self.state.player:
            self.say(f"{actor.name} gains {hp_gain} max HP.")
            for line in feature_lines:
                self.say(line)
            if self.level_up_skill_choices_for(actor):
                self.add_pending_player_level_up_skill_pick(new_level)
                self.say("New class skill training is waiting. Type `level` at any prompt to choose it.")
        else:
            picked = self.auto_choose_level_up_skill(actor)
            summary_parts = [f"{actor.name} gains {hp_gain} max HP"]
            if picked is not None:
                summary_parts.append(f"learns {skill_option_label(picked)}")
            self.say(", and ".join(summary_parts) + ".")
            for line in feature_lines:
                self.say(f"{actor.name}: {line}")

    def scale_level_resources(self, actor: Character, *, refill: bool = True) -> None:
        synchronize_spell_slots(actor, refill=refill)
        synchronize_magic_points(actor, refill=refill)
        synchronize_class_resources = getattr(self, "synchronize_class_resources", None)
        if callable(synchronize_class_resources):
            synchronize_class_resources(actor, refill=refill)

    def choose_level_up_skill(self, actor: Character) -> None:
        available = self.level_up_skill_choices_for(actor)
        if not available:
            self.say(f"{actor.name} has no new {class_label(actor.class_name)} skills available to learn.")
            return
        choice = self.choose(
            f"Choose a new {class_label(actor.class_name)} skill for {actor.name}.",
            [skill_option_label(skill) for skill in available],
            allow_meta=False,
        )
        picked = available[choice - 1]
        actor.skill_proficiencies.append(picked)
        actor.skill_proficiencies.sort()
        self.say(f"{actor.name} learns {skill_option_label(picked)}.")

    def auto_choose_level_up_skill(self, actor: Character) -> str | None:
        available = self.level_up_skill_choices_for(actor)
        if not available:
            return None
        picked = available[0]
        actor.skill_proficiencies.append(picked)
        actor.skill_proficiencies.sort()
        return picked

    def random_choose_level_up_skill(self, actor: Character) -> str | None:
        available = self.level_up_skill_choices_for(actor)
        if not available:
            return None
        picked = self.rng.choice(available)
        actor.skill_proficiencies.append(picked)
        actor.skill_proficiencies.sort()
        return picked

    def level_up_character_automatically(
        self,
        actor: Character,
        new_level: int,
        *,
        randomize_skill_choice: bool = False,
        announce: bool = True,
        allow_companion_subclass_choice: bool = False,
    ) -> None:
        actor.level = new_level
        hp_gain = max(1, actor.hit_die // 2 + 1 + actor.ability_mod("CON"))
        actor.max_hp += hp_gain
        actor.current_hp += hp_gain
        self.scale_level_resources(actor)
        self.ensure_companion_subclass(
            actor,
            allow_choice=allow_companion_subclass_choice,
            announce=announce or allow_companion_subclass_choice,
        )
        feature_lines = self.apply_class_level_features(actor, new_level, announce=False)
        picked = (
            self.random_choose_level_up_skill(actor)
            if randomize_skill_choice
            else self.auto_choose_level_up_skill(actor)
        )
        if announce:
            summary_parts = [f"{actor.name} gains {hp_gain} max HP"]
            if picked is not None:
                summary_parts.append(f"learns {skill_option_label(picked)}")
            self.say(", and ".join(summary_parts) + ".")
            for line in feature_lines:
                self.say(f"{actor.name}: {line}")
