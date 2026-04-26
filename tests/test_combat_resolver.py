from __future__ import annotations

import random
import unittest

from dnd_game.content import build_character
from dnd_game.game import TextDnDGame
from dnd_game.models import GameState


def build_game_with_player(class_name: str, scores: dict[str, int]) -> tuple[TextDnDGame, object]:
    player = build_character(
        name="Vale",
        race="Human",
        class_name=class_name,
        background="Soldier",
        base_ability_scores=scores,
        class_skill_choices=["Athletics", "Survival"],
    )
    game = TextDnDGame(input_fn=lambda _: "1", output_fn=lambda _: None, rng=random.Random(90101))
    game.state = GameState(player=player, current_scene="road_ambush")
    return game, player


class CombatResolverTests(unittest.TestCase):
    def test_accuracy_targets_avoidance_instead_of_armor_class(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        rogue_game, rogue = build_game_with_player(
            "Rogue",
            {"STR": 10, "DEX": 16, "CON": 13, "INT": 12, "WIS": 10, "CHA": 12},
        )

        self.assertEqual(fighter.armor_class, 18)
        self.assertEqual(game.effective_avoidance(fighter), 0)
        self.assertEqual(game.effective_attack_target_number(fighter), 10)
        self.assertEqual(rogue_game.effective_avoidance(rogue), 3)
        self.assertEqual(rogue_game.effective_attack_target_number(rogue), 13)

    def test_percentage_defense_reduces_physical_damage_after_resistance(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        fighter.gear_bonuses["resist_slashing"] = 1

        actual = game.apply_damage(fighter, 10, damage_type="slashing", apply_defense=True)

        result = game.last_damage_resolution()
        self.assertEqual(result.resisted_damage, 5)
        self.assertEqual(result.defense_percent, 40)
        self.assertEqual(actual, 3)
        self.assertTrue(result.wound)

    def test_armor_break_lowers_defense_by_percentage_points(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )

        actual = game.apply_damage(fighter, 10, damage_type="slashing", apply_defense=True, armor_break_percent=10)

        result = game.last_damage_resolution()
        self.assertEqual(result.armor_break_percent, 10)
        self.assertEqual(result.defense_percent, 30)
        self.assertEqual(actual, 7)

    def test_glance_and_wound_are_recorded_after_defense_and_temp_hp(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )

        glancing = game.apply_damage(fighter, 1, damage_type="slashing", apply_defense=True)
        glancing_result = game.last_damage_resolution()
        self.assertEqual(glancing, 0)
        self.assertTrue(glancing_result.glance)
        self.assertFalse(glancing_result.wound)

        fighter.temp_hp = 10
        absorbed = game.apply_damage(fighter, 10, damage_type="slashing", apply_defense=True)
        absorbed_result = game.last_damage_resolution()
        self.assertEqual(absorbed, 0)
        self.assertEqual(absorbed_result.temp_hp_absorbed, 6)
        self.assertFalse(absorbed_result.glance)
        self.assertFalse(absorbed_result.wound)

    def test_non_physical_spell_damage_bypasses_defense(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )

        actual = game.apply_damage(fighter, 10, damage_type="fire", apply_defense=True)

        result = game.last_damage_resolution()
        self.assertEqual(result.defense_percent, 0)
        self.assertEqual(actual, 10)


if __name__ == "__main__":
    unittest.main()
