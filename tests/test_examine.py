from __future__ import annotations

from types import SimpleNamespace
import unittest

from dnd_game.ui.examine import current_location_examine_entry, examine_entry_for_text, status_examine_entry


class ExamineEntryTests(unittest.TestCase):
    def test_story_skill_option_uses_skill_lore(self) -> None:
        entry = examine_entry_for_text("[ATHLETICS] *Hold the line.")

        self.assertEqual(entry.title, "Athletics")
        self.assertEqual(entry.category, "Story Skill Check")
        self.assertIn("body's answer", entry.description)
        self.assertTrue(any("Strength" in detail for detail in entry.details))

    def test_channel_option_uses_feature_description_and_cost(self) -> None:
        entry = examine_entry_for_text("Arcane Bolt (Action, 1 MP)")

        self.assertEqual(entry.title, "Arcane Bolt")
        self.assertEqual(entry.category, "Channel")
        self.assertIn("force damage", entry.description)
        self.assertIn("Cost: 1 MP", entry.details)

    def test_named_character_uses_game_intro_text(self) -> None:
        entry = examine_entry_for_text("Tessa Harrow")

        self.assertEqual(entry.title, "Tessa Harrow")
        self.assertEqual(entry.category, "Character")
        self.assertIn("Iron Hollow", entry.description)

    def test_class_selection_option_uses_class_lore_before_colon(self) -> None:
        entry = examine_entry_for_text("Warrior: d10 hit die. Hold the line.")

        self.assertEqual(entry.title, "Warrior")
        self.assertEqual(entry.category, "Class")
        self.assertTrue(any("d10" in detail for detail in entry.details))

    def test_status_entry_summarizes_status_definition(self) -> None:
        entry = status_examine_entry("Burning")

        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.title, "Burning")
        self.assertIn("ongoing", " ".join(entry.details).lower())

    def test_location_entry_uses_location_lore(self) -> None:
        entry = examine_entry_for_text("Glasswater Intake")

        self.assertEqual(entry.title, "Glasswater Intake")
        self.assertEqual(entry.category, "Location")
        self.assertIn("waterworks", entry.description)

    def test_current_location_entry_includes_scene_objective(self) -> None:
        game = SimpleNamespace(
            state=SimpleNamespace(current_scene="glasswater_intake"),
            SCENE_LABELS={"glasswater_intake": "Glasswater Intake"},
            SCENE_OBJECTIVES={"glasswater_intake": "Stabilize the headgate."},
        )

        entry = current_location_examine_entry(game)

        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.title, "Glasswater Intake")
        self.assertIn("Stabilize the headgate.", " ".join(entry.details))


if __name__ == "__main__":
    unittest.main()
