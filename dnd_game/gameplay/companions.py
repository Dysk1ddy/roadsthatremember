from __future__ import annotations

from ..data.story.companions import ACTIVE_COMPANION_LIMIT, COMPANION_PROFILES, PARTY_LIMIT, relationship_label
from ..items import EQUIPMENT_SLOTS, LEGACY_ITEM_NAMES, starter_item_ids_for_character


class CompanionSystemMixin:
    TRUSTED_COMPANION_COUNSEL_MODIFIER_ID = "trusted_companion_counsel"
    LOW_TRUST_TENSION_SKILLS = frozenset(
        {
            "Deception",
            "Insight",
            "Intimidation",
            "Performance",
            "Persuasion",
        }
    )

    def has_companion(self, name: str) -> bool:
        assert self.state is not None
        if any(companion.name == name for companion in self.state.all_companions()):
            return True
        return name in set(self.state.flags.get("departed_companions", []))

    def current_party_size(self) -> int:
        assert self.state is not None
        return len(self.state.party_members())

    def highest_active_party_level(self) -> int:
        assert self.state is not None
        return max(member.level for member in self.state.party_members())

    def active_companion_limit(self) -> int:
        return ACTIVE_COMPANION_LIMIT

    def all_companions(self):
        assert self.state is not None
        return self.state.all_companions()

    def find_companion(self, name: str):
        assert self.state is not None
        for companion in self.state.all_companions():
            if companion.name == name:
                return companion
        return None

    def relationship_label_for(self, companion) -> str:
        return relationship_label(companion.disposition)

    def relationship_threshold(self, companion, minimum: str) -> bool:
        order = {"Terrible": -2, "Bad": -1, "Neutral": 0, "Good": 1, "Great": 2, "Exceptional": 3}
        return order[self.relationship_label_for(companion)] >= order[minimum]

    def companion_profile(self, companion) -> dict[str, object]:
        if not getattr(companion, "companion_id", ""):
            return {}
        return COMPANION_PROFILES.get(companion.companion_id, {})

    def companion_assist_skills(self, companion) -> list[str]:
        profile = self.companion_profile(companion)
        return [str(skill) for skill in list(profile.get("assist_skills", ()))]

    def companion_camp_counsel(self, companion) -> dict[str, object]:
        profile = self.companion_profile(companion)
        raw = profile.get("camp_counsel", {})
        return dict(raw) if isinstance(raw, dict) else {}

    def companion_combat_opener(self, companion) -> dict[str, object]:
        profile = self.companion_profile(companion)
        raw = profile.get("combat_opener", {})
        return dict(raw) if isinstance(raw, dict) else {}

    def format_bonus_mapping(self, bonuses: dict[str, int]) -> str:
        return ", ".join(f"{key} {int(value):+d}" for key, value in sorted(bonuses.items())) or "none"

    def companion_mechanical_effect_lines(self, companion) -> list[str]:
        if not getattr(companion, "companion_id", ""):
            return []
        profile = self.companion_profile(companion)
        lines: list[str] = []
        great_bonuses = {
            str(key): int(value)
            for key, value in dict(profile.get("great_bonuses", {})).items()
            if int(value) != 0
        }
        exceptional_bonuses = {
            str(key): int(value)
            for key, value in dict(profile.get("exceptional_bonuses", {})).items()
            if int(value) != 0
        }
        assist_skills = self.companion_assist_skills(companion)
        opener = self.companion_combat_opener(companion)
        counsel = self.companion_camp_counsel(companion)
        if companion.disposition <= -3:
            lines.append("Low trust: may refuse roster calls and can create -1 tension on social checks.")
        if companion.disposition >= 6:
            if great_bonuses:
                lines.append(f"Great trust bonuses active: {self.format_bonus_mapping(great_bonuses)}.")
            if opener:
                lines.append(f"Combat opener active: {opener.get('name', 'trusted opener')}.")
            if assist_skills:
                lines.append(f"Skill assists active: {', '.join(assist_skills)} (+1, or +2 at Exceptional).")
            if counsel:
                bonuses = {
                    str(key): int(value)
                    for key, value in dict(counsel.get("bonuses", {})).items()
                    if int(value) != 0
                }
                lines.append(f"Camp counsel available: {counsel.get('name', 'trusted counsel')} ({self.format_bonus_mapping(bonuses)}).")
        else:
            unlocks: list[str] = []
            if great_bonuses:
                unlocks.append(f"Great trust bonuses: {self.format_bonus_mapping(great_bonuses)}")
            if opener:
                unlocks.append(f"opener: {opener.get('name', 'trusted opener')}")
            if assist_skills:
                unlocks.append(f"assists: {', '.join(assist_skills)}")
            if unlocks:
                lines.append("Next unlock at Great trust: " + "; ".join(unlocks) + ".")
        if companion.disposition >= 9 and exceptional_bonuses:
            lines.append(f"Exceptional trust bonuses active: {self.format_bonus_mapping(exceptional_bonuses)}.")
        return lines

    def record_companion_disposition_change(
        self,
        companion,
        *,
        delta: int,
        previous: int,
        reason: str,
    ) -> None:
        if self.state is None or not delta:
            return
        raw_changes = self.state.flags.get("companion_disposition_changes", [])
        changes = raw_changes if isinstance(raw_changes, list) else []
        changes.append(
            {
                "name": companion.name,
                "delta": int(delta),
                "previous": int(previous),
                "current": int(companion.disposition),
                "label": self.relationship_label_for(companion),
                "reason": str(reason),
            }
        )
        self.state.flags["companion_disposition_changes"] = changes[-24:]

    def record_companion_trust_event(self, text: str) -> None:
        if self.state is None:
            return
        raw_events = self.state.flags.get("companion_trust_events", [])
        events = raw_events if isinstance(raw_events, list) else []
        if text not in events:
            events.append(text)
        self.state.flags["companion_trust_events"] = events[-24:]

    def refresh_companion_state(self, companion) -> None:
        if not companion.companion_id:
            companion.relationship_bonuses = {}
            return
        profile = COMPANION_PROFILES.get(companion.companion_id, {})
        bonuses: dict[str, int] = {}
        if companion.disposition >= 6:
            bonuses.update(dict(profile.get("great_bonuses", {})))
        if companion.disposition >= 9:
            for key, value in dict(profile.get("exceptional_bonuses", {})).items():
                bonuses[key] = bonuses.get(key, 0) + value
        companion.relationship_bonuses = bonuses

    def adjust_companion_disposition(self, companion, delta: int, reason: str) -> None:
        previous = companion.disposition
        companion.disposition += delta
        self.refresh_companion_state(companion)
        self.record_companion_disposition_change(companion, delta=delta, previous=previous, reason=reason)
        label = self.relationship_label_for(companion)
        if delta:
            direction = "improves" if delta > 0 else "drops"
            self.say(f"{companion.name}'s trust {direction} ({reason}). Relationship: {label} ({companion.disposition}).")
        if previous < 6 <= companion.disposition:
            self.say(COMPANION_PROFILES[companion.companion_id]["great_dialogue"])
        if previous < 9 <= companion.disposition:
            self.say(COMPANION_PROFILES[companion.companion_id]["exceptional_dialogue"])
        if companion.disposition <= -6:
            self.force_companion_departure(companion, reason=reason)

    def force_companion_departure(self, companion, *, reason: str) -> None:
        assert self.state is not None
        self.state.companions = [member for member in self.state.companions if member is not companion]
        self.state.camp_companions = [member for member in self.state.camp_companions if member is not companion]
        departed = set(self.state.flags.get("departed_companions", []))
        departed.add(companion.name)
        self.state.flags["departed_companions"] = sorted(departed)
        self.say(f"{companion.name} decides they can no longer trust you and leaves the company.")
        self.add_journal(f"{companion.name} left the party after trust collapsed ({reason}).")

    def sync_companion_to_active_party_level(self, companion) -> bool:
        assert self.state is not None
        target_level = self.highest_active_party_level()
        if companion.level >= target_level:
            return False
        previous_level = companion.level
        for next_level in range(companion.level + 1, target_level + 1):
            self.level_up_character_automatically(companion, next_level, announce=False)
        self.say(f"{companion.name} catches up from level {previous_level} to level {target_level} to match the active party.")
        return True

    def recruit_companion(self, companion) -> None:
        assert self.state is not None
        if self.has_companion(companion.name):
            return
        self.introduce_character(companion)
        if not companion.equipment_slots:
            companion.equipment_slots = {slot: None for slot in EQUIPMENT_SLOTS}
            for slot, item_id in starter_item_ids_for_character(companion).items():
                companion.equipment_slots[slot] = item_id
                if item_id is not None:
                    self.state.inventory[item_id] = self.state.inventory.get(item_id, 0) + 1
        for legacy_name, quantity in list(companion.inventory.items()):
            item_id = LEGACY_ITEM_NAMES.get(legacy_name)
            if item_id is not None:
                self.state.inventory[item_id] = self.state.inventory.get(item_id, 0) + quantity
        companion.inventory.clear()
        self.refresh_companion_state(companion)
        if len(self.state.companions) >= ACTIVE_COMPANION_LIMIT:
            self.state.camp_companions.append(companion)
            self.add_journal(f"{companion.name} joined your wider company and was sent to camp because the active party is full.")
            self.say(f"{companion.name} joins your wider company, but the active party is full. They head to camp for now.")
        else:
            self.state.companions.append(companion)
            self.sync_companion_to_active_party_level(companion)
            self.add_journal(f"{companion.name} joined the active party.")
        self.sync_equipment(companion)

    def move_companion_to_camp(self, companion) -> None:
        assert self.state is not None
        if companion not in self.state.companions:
            return
        self.state.companions.remove(companion)
        self.state.camp_companions.append(companion)
        tutorial_tracker = getattr(self, "record_opening_tutorial_companion_event", None)
        if callable(tutorial_tracker):
            tutorial_tracker("moved_to_camp", companion_name=companion.name)
        self.say(f"{companion.name} heads back to camp and leaves the active party.")

    def move_companion_to_party(self, companion) -> bool:
        assert self.state is not None
        if companion not in self.state.camp_companions:
            return False
        if companion.disposition <= -3:
            self.say(f"{companion.name} refuses to rejoin the active party while trust is this strained.")
            self.record_companion_trust_event(
                f"{companion.name} refused an active-party call at {self.relationship_label_for(companion)} trust."
            )
            return False
        if len(self.state.companions) >= ACTIVE_COMPANION_LIMIT:
            self.say(f"The active party is already at the limit of {PARTY_LIMIT} total members.")
            return False
        self.state.camp_companions.remove(companion)
        self.state.companions.append(companion)
        self.sync_companion_to_active_party_level(companion)
        tutorial_tracker = getattr(self, "record_opening_tutorial_companion_event", None)
        if callable(tutorial_tracker):
            tutorial_tracker("moved_to_party", companion_name=companion.name)
        self.say(f"{companion.name} returns from camp and joins the active party.")
        return True

    def apply_scene_companion_support(self, scene_key: str) -> int:
        assert self.state is not None
        total_bonus = 0
        for companion in self.state.companions:
            if companion.disposition < 6 or not companion.companion_id:
                continue
            scene_support = COMPANION_PROFILES[companion.companion_id].get("scene_support", {}).get(scene_key)
            if scene_support is None:
                continue
            self.say(scene_support["text"])
            total_bonus += int(scene_support.get("hero_bonus", 0))
            for status, duration in dict(scene_support.get("ally_statuses", {})).items():
                self.apply_status(self.state.player, status, int(duration), source=companion.name)
            if companion.disposition >= 9 and scene_support.get("hero_bonus", 0):
                total_bonus += 1
        return total_bonus

    def companion_skill_check_assist(self, actor, skill: str, context: str) -> tuple[int, list[str]]:
        if self.state is None or not self.is_party_member_actor(actor):
            return (0, [])
        bonus = 0
        lines: list[str] = []
        for companion in self.state.companions:
            if companion is actor or not companion.is_conscious() or not companion.companion_id:
                continue
            if companion.disposition >= 6 and skill in self.companion_assist_skills(companion):
                candidate = 2 if companion.disposition >= 9 else 1
                if candidate > bonus:
                    bonus = candidate
                    lines = [
                        f"{companion.name} assists the {skill} check with {self.relationship_label_for(companion).lower()} trust ({candidate:+d})."
                    ]
        penalty = 0
        for companion in self.state.companions:
            if companion is actor or not companion.is_conscious() or not companion.companion_id:
                continue
            if companion.disposition <= -3 and self.low_trust_tension_applies(skill, context):
                penalty = -1
                lines.append(f"{companion.name} argues the approach and creates trust tension ({penalty:+d}).")
                self.record_companion_trust_event(
                    f"{companion.name} created -1 tension on a {skill} check while trust was {self.relationship_label_for(companion)}."
                )
                break
        return (bonus + penalty, lines)

    def low_trust_tension_applies(self, skill: str, context: str) -> bool:
        if skill in self.LOW_TRUST_TENSION_SKILLS:
            return True
        lowered = context.lower()
        return any(token in lowered for token in ("convince", "calm", "trust", "parley", "argue", "promise"))

    def companion_status_line(self, companion) -> str:
        location = "Active party" if companion in self.state.companions else "Camp"
        if companion.dead:
            location = f"Dead ({location})"
        return (
            f"{companion.name}: Level {companion.level} {companion.race} {companion.class_name} | "
            f"{self.format_health_bar(companion.current_hp, companion.max_hp)}{self.health_status_suffix(companion.current_hp, dead=companion.dead)} | "
            f"{self.relationship_label_for(companion)} ({companion.disposition}) | {location}"
        )
