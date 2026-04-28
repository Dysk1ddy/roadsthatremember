from __future__ import annotations

import random
import unittest

from dnd_game.content import build_character, create_enemy
from dnd_game.game import TextDnDGame
from dnd_game.gameplay.combat_simulator import EncounterPassSimulation, simulate_encounter_pass
from dnd_game.models import GameState


def build_level_four_mixed_party() -> tuple[TextDnDGame, list[object]]:
    warrior = build_character(
        name="Vale",
        race="Human",
        class_name="Warrior",
        background="Soldier",
        base_ability_scores={"STR": 15, "DEX": 12, "CON": 14, "INT": 8, "WIS": 12, "CHA": 10},
        class_skill_choices=["Athletics", "Survival"],
    )
    rogue = build_character(
        name="Kael",
        race="Human",
        class_name="Rogue",
        background="Criminal",
        base_ability_scores={"STR": 10, "DEX": 16, "CON": 13, "INT": 12, "WIS": 10, "CHA": 12},
        class_skill_choices=["Stealth", "Sleight of Hand"],
    )
    mage = build_character(
        name="Mira",
        race="Human",
        class_name="Mage",
        background="Sage",
        base_ability_scores={"STR": 8, "DEX": 14, "CON": 13, "INT": 16, "WIS": 12, "CHA": 10},
        class_skill_choices=["Arcana", "Insight"],
    )
    game = TextDnDGame(input_fn=lambda _: "1", output_fn=lambda _: None, rng=random.Random(49217))
    party = [warrior, rogue, mage]
    game.state = GameState(player=warrior, companions=[rogue, mage], current_scene="encounter_pass")
    game._in_combat = True
    game._active_round_number = 1
    game._active_combat_heroes = party
    for member in party:
        for level in (2, 3, 4):
            game.level_up_character_automatically(member, level, announce=False)
        game.prepare_class_resources_for_combat(member)
    return game, party


class FullEncounterPassTests(unittest.TestCase):
    def scenario_result(self, name: str, enemies: list[object]) -> EncounterPassSimulation:
        game, party = build_level_four_mixed_party()
        game._active_combat_enemies = enemies
        return simulate_encounter_pass(game, name, party, enemies)

    def test_full_encounter_pass_covers_required_enemy_shapes(self) -> None:
        game, party = build_level_four_mixed_party()
        shieldhand = create_enemy("rukhar", name="Ashen Brand Shieldhand")
        game.apply_status(shieldhand, "raised_shield", 2, source="shield wall drill")
        scenarios = {
            "basic raiders": [create_enemy("bandit"), create_enemy("bandit_archer"), create_enemy("goblin_skirmisher")],
            "shieldhands": [shieldhand, create_enemy("ash_brand_enforcer")],
            "high-Avoidance scouts": [create_enemy("false_map_skirmisher"), create_enemy("blackglass_listener")],
            "high-Defense brutes": [create_enemy("animated_armor"), create_enemy("blacklake_pincerling")],
            "Sereth-style named enemy": [create_enemy("sereth_vane"), create_enemy("bandit"), create_enemy("bandit_archer")],
        }

        results = {
            name: simulate_encounter_pass(game, name, party, enemies)
            for name, enemies in scenarios.items()
        }

        for name, result in results.items():
            with self.subTest(name=name):
                self.assertGreaterEqual(len(result.party_actions), 3)
                self.assertTrue(any(action.action_name.endswith("Arcane Bolt") for action in result.party_actions))
                self.assertGreater(result.party_expected_damage_per_round, 8.0)
                self.assertGreater(result.enemy_expected_damage_per_round, 1.0)
                self.assertLess(result.rounds_to_clear, result.rounds_to_party_defeat)
                self.assertGreater(result.survival_margin_rounds, 1.0)

        self.assertLessEqual(results["basic raiders"].max_enemy_defense_percent, 15)
        self.assertGreaterEqual(results["shieldhands"].max_enemy_defense_percent, 40)
        self.assertGreaterEqual(results["high-Avoidance scouts"].max_enemy_avoidance, 3)
        self.assertGreaterEqual(results["high-Defense brutes"].max_enemy_defense_percent, 40)
        self.assertIn("Sereth Vane", results["Sereth-style named enemy"].enemy_names)

    def test_full_encounter_pass_boss_armor_break_weakness_moves_the_numbers(self) -> None:
        game, party = build_level_four_mixed_party()
        boss = create_enemy("pact_archive_warden", name="Ledger-Bound Bulwark")

        base = simulate_encounter_pass(game, "boss baseline", party, [boss])
        broken = simulate_encounter_pass(
            game,
            "boss Armor Break weakness",
            party,
            [boss],
            party_armor_break_percent=20,
        )

        self.assertEqual(base.max_enemy_defense_percent, 55)
        self.assertGreater(broken.party_expected_damage_per_round, base.party_expected_damage_per_round)
        self.assertLess(broken.rounds_to_clear, base.rounds_to_clear * 0.9)
        self.assertTrue(
            any(
                action.armor_break_percent >= 20 and action.defense_percent <= 35
                for action in broken.party_actions
                if action.action_name.startswith("Weapon:")
            )
        )


if __name__ == "__main__":
    unittest.main()
