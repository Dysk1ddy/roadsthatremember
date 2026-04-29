from __future__ import annotations

import random
import unittest

from dnd_game.content import build_character, create_elira_dawnmantle, create_tolan_ironshield
from dnd_game.data.quests import QuestLogEntry
from dnd_game.game import TextDnDGame
from dnd_game.items import get_item
from dnd_game.models import GameState
from dnd_game.ui.command_snapshots import (
    build_camp_snapshot,
    build_gear_snapshot,
    build_inventory_snapshot,
    build_journal_snapshot,
)
from dnd_game.ui.command_actions import (
    drop_inventory_item,
    equip_item_for_member,
    take_long_rest,
    take_short_rest,
    unequip_member_slot,
    use_inventory_item_on_target,
)


def make_player():
    return build_character(
        name="Vale",
        race="Human",
        class_name="Warrior",
        background="Soldier",
        base_ability_scores={"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        class_skill_choices=["Athletics", "Survival"],
    )


def make_snapshot_game() -> TextDnDGame:
    player = make_player()
    companion = create_tolan_ironshield()
    game = TextDnDGame(input_fn=lambda _: "1", output_fn=lambda _: None, rng=random.Random(91234))
    game.state = GameState(
        player=player,
        companions=[companion],
        camp_companions=[create_elira_dawnmantle()],
        current_scene="iron_hollow_hub",
        gold=125,
        inventory={
            "potion_healing": 2,
            "travel_biscuits": 3,
            "longsword_common": 2,
            "iron_cap_common": 1,
        },
        quests={
            "secure_miners_road": QuestLogEntry(
                quest_id="secure_miners_road",
                notes=["Tessa wants the east road cleared."],
            )
        },
    )
    game.add_journal("You promised Tessa the road would breathe again.")
    game.add_clue("Ashfall Watch runners marked wagons before dusk.")
    game.ensure_state_integrity()
    return game


class CommandSnapshotTests(unittest.TestCase):
    def test_inventory_snapshot_counts_filters_and_selected_item(self) -> None:
        game = make_snapshot_game()

        snapshot = build_inventory_snapshot(game, filter_key="consumables", selected_item_id="potion_healing")

        self.assertEqual(snapshot.filter_label, "Consumables")
        self.assertEqual(snapshot.gold, 125)
        self.assertGreaterEqual(snapshot.supply_points, 3)
        potion_name = get_item("potion_healing").name
        self.assertEqual([item.name for item in snapshot.items], [potion_name])
        self.assertIsNotNone(snapshot.selected_item)
        assert snapshot.selected_item is not None
        self.assertEqual(snapshot.selected_item.name, potion_name)
        self.assertTrue(snapshot.selected_item.usable)
        self.assertGreaterEqual(snapshot.selected_item.available, 2)
        counts = {filter_snapshot.key: filter_snapshot.count for filter_snapshot in snapshot.filters}
        self.assertGreaterEqual(counts["all"], 4)
        self.assertEqual(counts["consumables"], 1)

    def test_gear_snapshot_lists_slots_candidates_and_comparisons_without_equipping(self) -> None:
        game = make_snapshot_game()
        assert game.state is not None
        before_slots = dict(game.state.player.equipment_slots)

        snapshot = build_gear_snapshot(game, selected_member_index=0, selected_slot="head")

        self.assertEqual(snapshot.members[0].name, "Vale")
        head_slot = next(slot for slot in snapshot.members[0].slots if slot.slot == "head")
        self.assertEqual(head_slot.current_name, "Empty")
        iron_cap_name = get_item("iron_cap_common").name
        self.assertTrue(any(candidate.name == iron_cap_name for candidate in head_slot.candidates))
        candidate = next(candidate for candidate in head_slot.candidates if candidate.name == iron_cap_name)
        self.assertIn("Defense", candidate.comparison)
        self.assertEqual(dict(game.state.player.equipment_slots), before_slots)

    def test_journal_snapshot_collects_quest_clue_and_recent_update_sections(self) -> None:
        game = make_snapshot_game()

        snapshot = build_journal_snapshot(game)

        self.assertEqual(snapshot.location, "Iron Hollow")
        self.assertEqual(len(snapshot.active_quests), 1)
        self.assertEqual(snapshot.active_quests[0].title, "Stop the Watchtower Raids")
        self.assertTrue(any("Ashfall Watch" in clue for clue in snapshot.unresolved_clues))
        self.assertTrue(any("Tessa" in update for update in snapshot.recent_updates))
        self.assertEqual(snapshot.empty_message, "")

    def test_camp_snapshot_summarizes_roster_resources_and_actions(self) -> None:
        game = make_snapshot_game()

        snapshot = build_camp_snapshot(game)

        self.assertEqual(snapshot.gold_label, "125 gold")
        self.assertEqual(snapshot.active_party_count, 2)
        self.assertEqual(snapshot.camp_roster_count, 1)
        self.assertTrue(any("Vale" in line for line in snapshot.active_party))
        self.assertTrue(any("Elira" in line for line in snapshot.camp_roster))
        action_labels = [action.label for action in snapshot.actions]
        self.assertIn("Supplies and equipment", action_labels)
        self.assertIn("Break camp", action_labels)

    def test_native_gear_actions_equip_and_unequip_without_prompting(self) -> None:
        game = make_snapshot_game()
        assert game.state is not None
        item_id = get_item("iron_cap_common").item_id

        equipped = equip_item_for_member(game, 0, "head", item_id)

        self.assertTrue(equipped.ok)
        self.assertEqual(get_item(game.state.player.equipment_slots["head"]).name, get_item(item_id).name)

        unequipped = unequip_member_slot(game, 0, "head")

        self.assertTrue(unequipped.ok)
        self.assertIsNone(game.state.player.equipment_slots["head"])

    def test_native_inventory_actions_use_and_drop_items(self) -> None:
        game = make_snapshot_game()
        assert game.state is not None
        potion_id = get_item("potion_healing").item_id
        game.state.player.current_hp = 1
        before_count = game.inventory_dict().get(potion_id, 0)

        used = use_inventory_item_on_target(game, potion_id, 0)

        self.assertTrue(used.ok)
        self.assertGreater(game.state.player.current_hp, 1)
        self.assertEqual(game.inventory_dict().get(potion_id, 0), before_count - 1)

        dropped = drop_inventory_item(game, potion_id, 1)

        self.assertTrue(dropped.ok)
        self.assertEqual(game.inventory_dict().get(potion_id, 0), before_count - 2)

    def test_native_camp_rest_actions_apply_recovery_and_supply_rules(self) -> None:
        game = make_snapshot_game()
        assert game.state is not None
        game.state.player.current_hp = 1
        game.state.short_rests_remaining = 1

        short_rest = take_short_rest(game)

        self.assertTrue(short_rest.ok)
        self.assertGreater(game.state.player.current_hp, 1)
        self.assertEqual(game.state.short_rests_remaining, 0)

        game.state.player.current_hp = 1
        game.state.inventory = {"travel_biscuits": 12}
        game.ensure_state_integrity()

        long_rest = take_long_rest(game)

        self.assertTrue(long_rest.ok)
        self.assertEqual(game.state.player.current_hp, game.state.player.max_hp)
        self.assertEqual(game.state.short_rests_remaining, 2)


if __name__ == "__main__":
    unittest.main()
