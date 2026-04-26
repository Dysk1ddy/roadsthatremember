from __future__ import annotations

import random
import unittest

from dnd_game.content import build_character
from dnd_game.content import create_enemy
from dnd_game.data.items.catalog import ITEMS, item_rules_text
from dnd_game.data.story.factories import LOW_LEVEL_ENEMY_COMBAT_PROFILES
from dnd_game.dice import D20Outcome, RollOutcome
from dnd_game.game import TextDnDGame
from dnd_game.gameplay.combat_simulator import simulate_weapon_attack
from dnd_game.gameplay.encounter import Encounter
from dnd_game.models import Armor, GameState, Weapon


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
    def test_catalog_armor_and_shields_emit_percent_defense(self) -> None:
        self.assertEqual(ITEMS["traveler_clothes_common"].armor.defense_percent, 0)
        self.assertEqual(ITEMS["leather_armor_common"].armor.defense_percent, 10)
        self.assertEqual(ITEMS["studded_leather_common"].armor.defense_percent, 15)
        self.assertEqual(ITEMS["chain_mail_common"].armor.defense_percent, 35)
        self.assertEqual(ITEMS["chain_mail_rare"].armor.defense_percent, 40)
        self.assertEqual(ITEMS["breastplate_epic"].armor.defense_percent, 40)
        self.assertEqual(ITEMS["splint_armor_legendary"].armor.defense_percent, 60)

        self.assertEqual(ITEMS["chain_mail_rare"].armor.base_ac, 16)
        self.assertEqual(ITEMS["chain_mail_rare"].armor.defense_cap_percent, 75)
        self.assertEqual(ITEMS["shield_common"].shield_defense_percent, 5)
        self.assertEqual(ITEMS["shield_rare"].shield_defense_percent, 10)
        self.assertEqual(ITEMS["shield_rare"].raised_shield_defense_percent, 10)
        self.assertIn("Defense 35%", item_rules_text(ITEMS["chain_mail_common"]))
        self.assertIn("shield Defense +5%", item_rules_text(ITEMS["shield_common"]))

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

    def test_equipment_sync_converts_old_ac_gear_to_percent_defense(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        fighter.equipment_slots = {
            "head": "iron_cap_common",
            "ring_1": None,
            "ring_2": None,
            "neck": None,
            "chest": "chain_mail_common",
            "gloves": None,
            "boots": None,
            "main_hand": "longsword_common",
            "off_hand": "shield_common",
            "cape": None,
        }

        game.sync_equipment(fighter)

        self.assertNotIn("AC", fighter.gear_bonuses)
        self.assertEqual(fighter.gear_bonuses["defense_percent"], 5)
        self.assertEqual(fighter.gear_bonuses["shield_defense_percent"], 5)
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 45)

    def test_raised_shield_adds_temporary_percent_defense(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        enemy = create_enemy("bandit")
        encounter = Encounter("Sparring", "A shield drill.", [enemy])

        self.assertIn("Raise Shield", game.get_player_combat_options(fighter, encounter, heroes=[fighter]))
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 40)

        game.use_raise_shield(fighter)

        self.assertTrue(game.has_status(fighter, "raised_shield"))
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 50)
        self.assertNotIn("Raise Shield", game.get_player_combat_options(fighter, encounter, heroes=[fighter]))

    def test_combat_stances_are_mutually_exclusive_and_adjust_stats(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )

        self.assertEqual(game.current_combat_stance_key(fighter), "neutral")
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 40)
        self.assertEqual(game.effective_avoidance(fighter), 0)
        self.assertEqual(game.effective_stability(fighter), 3)

        game.set_combat_stance(fighter, "guard")
        self.assertEqual(game.current_combat_stance_key(fighter), "guard")
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 60)
        self.assertEqual(game.effective_avoidance(fighter), 1)
        self.assertEqual(game.effective_stability(fighter), 5)
        self.assertEqual(game.status_accuracy_modifier(fighter), -2)

        game.set_combat_stance(fighter, "brace")
        self.assertEqual(game.current_combat_stance_key(fighter), "brace")
        self.assertFalse(game.has_status(fighter, "stance_guard"))
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 50)
        self.assertEqual(game.effective_avoidance(fighter), -1)
        self.assertEqual(game.effective_stability(fighter), 7)
        self.assertEqual(game.status_accuracy_modifier(fighter), -1)

        game.set_combat_stance(fighter, "mobile")
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 35)
        self.assertEqual(game.effective_avoidance(fighter), 2)
        self.assertEqual(game.effective_stability(fighter), 2)
        self.assertEqual(game.status_value(fighter, "flee_bonus"), 2)

        game.set_combat_stance(fighter, "aggressive")
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 30)
        self.assertEqual(game.effective_avoidance(fighter), -1)
        self.assertEqual(game.status_accuracy_modifier(fighter), 2)
        self.assertEqual(game.status_damage_modifier(fighter), 2)

        game.set_combat_stance(fighter, "aim")
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 35)
        self.assertEqual(game.effective_avoidance(fighter), -2)
        self.assertEqual(game.effective_stability(fighter), 2)
        self.assertEqual(game.status_accuracy_modifier(fighter), 2)

        game.set_combat_stance(fighter, "neutral")
        self.assertEqual(game.current_combat_stance_key(fighter), "neutral")
        self.assertEqual(game.effective_defense_percent(fighter, damage_type="slashing"), 40)

    def test_press_stance_applies_outgoing_armor_break_without_self_vulnerability(self) -> None:
        game, attacker = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        _, target = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )

        game.set_combat_stance(attacker, "press")
        self.assertEqual(game.effective_defense_percent(attacker, damage_type="slashing"), 35)
        self.assertEqual(game.effective_defense_percent(target, damage_type="slashing"), 40)

        actual = game.apply_damage(target, 10, damage_type="slashing", source_actor=attacker, apply_defense=True)

        result = game.last_damage_resolution()
        self.assertEqual(result.armor_break_percent, 10)
        self.assertEqual(result.defense_percent, 30)
        self.assertEqual(actual, 7)

    def test_player_can_choose_combat_stance_as_bonus_action(self) -> None:
        answers = iter(["2"])
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        game.input_fn = lambda _: next(answers)

        self.assertTrue(game.choose_combat_stance(fighter))

        self.assertEqual(game.current_combat_stance_key(fighter), "guard")

    def test_enemy_ai_selects_press_against_high_defense_target(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        enemy = create_enemy("bandit")

        game.maybe_apply_enemy_stance(enemy, fighter, [fighter], [])

        self.assertEqual(game.current_combat_stance_key(enemy), "press")

    def test_level_one_raiders_use_explicit_avoidance_and_defense_bands(self) -> None:
        game, _ = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        bandit = create_enemy("bandit")
        archer = create_enemy("bandit_archer")
        scuttler = create_enemy("rust_shell_scuttler")

        self.assertEqual(game.effective_defense_percent(bandit, damage_type="slashing"), 10)
        self.assertEqual(game.effective_avoidance(bandit), 1)
        self.assertEqual(game.effective_attack_target_number(bandit), 11)
        self.assertEqual(game.effective_defense_percent(archer, damage_type="slashing"), 5)
        self.assertEqual(game.effective_avoidance(archer), 2)
        self.assertEqual(game.effective_defense_percent(scuttler, damage_type="slashing"), 20)
        self.assertEqual(game.effective_avoidance(scuttler), 1)

    def test_low_level_scout_brute_shieldhand_and_named_profiles_are_converted(self) -> None:
        game, _ = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        cases = {
            "false_map_skirmisher": (10, 4),
            "ogre_brute": (15, -1),
            "rukhar": (30, 1),
            "sereth_vane": (15, 3),
        }

        for template, (defense, avoidance) in cases.items():
            with self.subTest(template=template):
                enemy = create_enemy(template)
                self.assertEqual(game.effective_defense_percent(enemy, damage_type="slashing"), defense)
                self.assertEqual(game.effective_avoidance(enemy), avoidance)
                self.assertEqual(enemy.bond_flags["combat_profile"]["defense_percent"], defense)
                self.assertEqual(enemy.bond_flags["combat_profile"]["avoidance"], avoidance)

    def test_high_defense_enemies_stay_rare_before_level_four(self) -> None:
        game, _ = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        high_defense_before_four: list[str] = []
        high_defense_at_four: set[str] = set()
        for template in LOW_LEVEL_ENEMY_COMBAT_PROFILES:
            enemy = create_enemy(template)
            defense = game.effective_defense_percent(enemy, damage_type="slashing")
            if enemy.level < 4 and defense >= 35:
                high_defense_before_four.append(template)
            if enemy.level == 4 and defense >= 35:
                high_defense_at_four.add(template)

        self.assertEqual(high_defense_before_four, ["animated_armor"])
        self.assertEqual(high_defense_at_four, {"pact_archive_warden", "blacklake_pincerling", "graveblade_wight"})

    def test_all_level_one_to_four_profiles_apply_exact_targets(self) -> None:
        game, _ = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        for template, profile in LOW_LEVEL_ENEMY_COMBAT_PROFILES.items():
            with self.subTest(template=template):
                enemy = create_enemy(template)
                self.assertLessEqual(enemy.level, 4)
                self.assertEqual(
                    game.effective_defense_percent(enemy, damage_type="slashing"),
                    profile["defense_percent"],
                )
                self.assertEqual(game.effective_avoidance(enemy), profile["avoidance"])

    def test_combat_simulator_reports_exact_hit_chance_against_avoidance(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        bandit = create_enemy("bandit")
        skirmisher = create_enemy("false_map_skirmisher")

        bandit_result = simulate_weapon_attack(game, fighter, bandit)
        skirmisher_result = simulate_weapon_attack(game, fighter, skirmisher)

        self.assertEqual(bandit_result.target_number, 11)
        self.assertEqual(bandit_result.accuracy_bonus, 5)
        self.assertAlmostEqual(bandit_result.miss_chance, 0.25)
        self.assertAlmostEqual(bandit_result.normal_hit_chance, 0.70)
        self.assertAlmostEqual(bandit_result.critical_chance, 0.05)
        self.assertAlmostEqual(bandit_result.hit_chance, 0.75)
        self.assertEqual(skirmisher_result.target_number, 14)
        self.assertAlmostEqual(skirmisher_result.hit_chance, 0.60)

    def test_combat_simulator_expected_damage_uses_percentage_defense(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        bandit = create_enemy("bandit")

        result = simulate_weapon_attack(game, fighter, bandit)

        self.assertEqual(result.damage.defense_percent, 10)
        self.assertEqual(result.damage.armor_break_percent, 0)
        self.assertAlmostEqual(result.damage.expected_hp_damage_on_normal_hit, 6.375)
        self.assertAlmostEqual(result.damage.expected_hp_damage_on_critical_hit, 10.328125)
        self.assertAlmostEqual(result.expected_hp_damage, 4.97890625)

    def test_combat_simulator_guard_stance_reduces_incoming_weapon_damage(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        bandit = create_enemy("bandit")

        base = simulate_weapon_attack(game, bandit, fighter, heroes=[bandit], enemies=[])
        game.set_combat_stance(fighter, "guard", announce=False)
        guarded = simulate_weapon_attack(game, bandit, fighter, heroes=[bandit], enemies=[])

        self.assertEqual(base.target_number, 10)
        self.assertEqual(base.damage.defense_percent, 40)
        self.assertAlmostEqual(base.hit_chance, 0.70)
        self.assertAlmostEqual(base.expected_hp_damage, 1.7361111111111112)
        self.assertEqual(guarded.target_number, 11)
        self.assertEqual(guarded.damage.defense_percent, 60)
        self.assertAlmostEqual(guarded.hit_chance, 0.65)
        self.assertAlmostEqual(guarded.expected_hp_damage, 0.9402777777777778)
        self.assertLess(guarded.expected_hp_damage, base.expected_hp_damage)

    def test_combat_simulator_armor_break_raises_expected_damage(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        animated_armor = create_enemy("animated_armor")

        armored = simulate_weapon_attack(game, fighter, animated_armor)
        broken = simulate_weapon_attack(game, fighter, animated_armor, armor_break_percent=20)

        self.assertEqual(armored.damage.defense_percent, 35)
        self.assertEqual(broken.damage.armor_break_percent, 20)
        self.assertEqual(broken.damage.defense_percent, 15)
        self.assertAlmostEqual(armored.expected_hp_damage, 3.86640625)
        self.assertAlmostEqual(broken.expected_hp_damage, 5.1859375)
        self.assertGreater(broken.expected_hp_damage, armored.expected_hp_damage)

    def test_combat_simulator_tracks_glance_without_wound(self) -> None:
        game, attacker = build_game_with_player(
            "Fighter",
            {"STR": 10, "DEX": 10, "CON": 10, "INT": 8, "WIS": 10, "CHA": 10},
        )
        _, target = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        attacker.weapon = Weapon(name="Needle", damage="1d1", ability="STR")
        target.armor = Armor(
            name="Test Plate",
            base_ac=16,
            dex_cap=0,
            heavy=True,
            defense_percent=75,
            defense_cap_percent=75,
        )
        target.shield = False
        target.equipment_bonuses.clear()
        target.gear_bonuses.clear()
        target.relationship_bonuses.clear()

        result = simulate_weapon_attack(game, attacker, target)

        self.assertEqual(result.damage.defense_percent, 75)
        self.assertAlmostEqual(result.expected_hp_damage, 0.0)
        self.assertAlmostEqual(result.glance_chance, result.hit_chance)
        self.assertAlmostEqual(result.wound_chance, 0.0)

    def test_wound_riders_require_hp_damage_after_glance(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        fighter.armor = Armor(
            name="Test Plate",
            base_ac=16,
            dex_cap=0,
            heavy=True,
            defense_percent=75,
            defense_cap_percent=75,
        )
        fighter.shield = False
        fighter.equipment_bonuses.clear()
        fighter.gear_bonuses.clear()
        fighter.relationship_bonuses.clear()
        stalker = create_enemy("carrion_stalker")
        stalker.weapon = Weapon(name="Serrated Talon", damage="1d1", ability="STR")
        game.roll_check_d20 = lambda *args, **kwargs: D20Outcome(kept=15, rolls=[15], advantage_state=0)  # type: ignore[method-assign]
        game.roll_with_display_bonus = lambda expression, *args, **kwargs: RollOutcome(expression, 1, [1], 0)  # type: ignore[method-assign]

        game.perform_enemy_attack(stalker, fighter, [fighter], [stalker], set())

        self.assertTrue(game.last_damage_was_glance())
        self.assertFalse(game.last_damage_caused_wound())
        self.assertFalse(game.has_status(fighter, "bleeding"))

        fighter.armor.defense_percent = 0
        fighter.armor.defense_cap_percent = 75
        game.perform_enemy_attack(stalker, fighter, [fighter], [stalker], set())

        self.assertFalse(game.last_damage_was_glance())
        self.assertTrue(game.last_damage_caused_wound())
        self.assertTrue(game.has_status(fighter, "bleeding"))

    def test_shared_class_framework_prepares_grit_edge_satchel_toxin_and_ward(self) -> None:
        game, warrior = build_game_with_player(
            "Warrior",
            {"STR": 15, "DEX": 12, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        _, rogue = build_game_with_player(
            "Rogue",
            {"STR": 10, "DEX": 16, "CON": 13, "INT": 12, "WIS": 10, "CHA": 12},
        )
        _, wizard = build_game_with_player(
            "Wizard",
            {"STR": 8, "DEX": 14, "CON": 13, "INT": 16, "WIS": 12, "CHA": 10},
        )
        wizard.features.append("mage_ward")

        for actor in (warrior, rogue, wizard):
            game.prepare_class_resources_for_combat(actor)

        self.assertEqual(warrior.max_resources["grit"], 6)
        self.assertEqual(warrior.resources["grit"], 1)
        self.assertEqual(rogue.max_resources["edge"], 5)
        self.assertEqual(rogue.resources["edge"], 1)
        self.assertEqual(rogue.max_resources["satchel"], 5)
        self.assertEqual(rogue.resources["satchel"], 5)
        self.assertEqual(rogue.max_resources["toxin"], 5)
        self.assertEqual(rogue.resources["toxin"], 0)
        self.assertEqual(wizard.max_resources["ward"], 12)
        self.assertEqual(wizard.resources["ward"], 0)

    def test_ward_absorbs_after_defense_before_temp_hp(self) -> None:
        game, fighter = build_game_with_player(
            "Fighter",
            {"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        fighter.features.append("mage_ward")
        game.synchronize_class_resources(fighter, refill=True)
        fighter.temp_hp = 10

        game.grant_ward(fighter, 4, source="test shell")
        actual = game.apply_damage(fighter, 10, damage_type="slashing", apply_defense=True)

        result = game.last_damage_resolution()
        self.assertEqual(result.defense_percent, 40)
        self.assertEqual(result.mitigated_damage, 6)
        self.assertEqual(result.ward_absorbed, 4)
        self.assertEqual(result.temp_hp_absorbed, 2)
        self.assertEqual(actual, 0)
        self.assertFalse(result.glance)
        self.assertFalse(result.wound)
        self.assertEqual(fighter.resources["ward"], 0)
        self.assertEqual(fighter.temp_hp, 8)

    def test_rogue_mark_poison_and_wound_hooks_award_resources(self) -> None:
        game, rogue = build_game_with_player(
            "Rogue",
            {"STR": 10, "DEX": 16, "CON": 13, "INT": 12, "WIS": 10, "CHA": 12},
        )
        target = create_enemy("bandit")
        game._in_combat = True
        game.prepare_class_resources_for_combat(rogue)

        game.mark_class_target(rogue, target)
        stacks = game.add_rogue_poison_stack(rogue, target)
        actual = game.apply_damage(target, 10, damage_type="piercing", source_actor=rogue, apply_defense=True)

        self.assertEqual(stacks, 1)
        self.assertTrue(game.target_is_marked_by(rogue, target))
        self.assertTrue(game.has_status(target, "poisoned"))
        self.assertGreater(actual, 0)
        self.assertTrue(game.last_damage_caused_wound())
        self.assertEqual(rogue.resources["edge"], 2)
        self.assertEqual(rogue.resources["toxin"], 1)
        self.assertEqual(target.bond_flags["class_mark_last_wounded_by"], rogue.name)

    def test_on_hit_hook_grants_edge_against_exposed_target(self) -> None:
        game, rogue = build_game_with_player(
            "Rogue",
            {"STR": 10, "DEX": 16, "CON": 13, "INT": 12, "WIS": 10, "CHA": 12},
        )
        target = create_enemy("bandit")
        game._in_combat = True
        game.prepare_class_resources_for_combat(rogue)
        game.apply_status(target, "reeling", 1, source="test setup")

        game.trigger_on_hit_hooks(
            rogue,
            target,
            actual_damage=3,
            margin=1,
            critical_hit=False,
            heroes=[rogue],
            enemies=[target],
        )

        self.assertEqual(rogue.resources["edge"], 2)

    def test_stance_upgrade_and_reaction_hooks_are_data_driven(self) -> None:
        game, warrior = build_game_with_player(
            "Warrior",
            {"STR": 15, "DEX": 12, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        game._in_combat = True
        game._active_round_number = 1
        game.prepare_class_resources_for_combat(warrior)
        warrior.bond_flags["stance_upgrades"] = {
            "guard": {
                "statuses": {"guarded": 1},
                "resources": {"grit": 1},
            }
        }

        game.set_combat_stance(warrior, "guard", announce=False)

        self.assertTrue(game.has_status(warrior, "guarded"))
        self.assertEqual(warrior.resources["grit"], 2)
        self.assertTrue(game.can_use_class_reaction(warrior))
        self.assertTrue(game.spend_class_reaction(warrior, source="test reaction"))
        self.assertFalse(game.can_use_class_reaction(warrior))
        self.assertFalse(game.spend_class_reaction(warrior, source="test reaction"))
        game._active_round_number = 2
        self.assertTrue(game.can_use_class_reaction(warrior))

    def test_class_combat_cleanup_clears_temporary_resources_marks_and_reactions(self) -> None:
        game, rogue = build_game_with_player(
            "Rogue",
            {"STR": 10, "DEX": 16, "CON": 13, "INT": 12, "WIS": 10, "CHA": 12},
        )
        target = create_enemy("bandit")
        game._in_combat = True
        game._active_round_number = 1
        game.prepare_class_resources_for_combat(rogue)
        game.mark_class_target(rogue, target)
        game.add_rogue_poison_stack(rogue, target)
        game.grant_class_resource(rogue, "toxin", source="test")
        game.spend_class_reaction(rogue, source="test")

        game.clear_after_encounter([rogue, target])

        self.assertEqual(rogue.resources["edge"], 0)
        self.assertEqual(rogue.resources["toxin"], 0)
        self.assertEqual(rogue.resources["satchel"], rogue.max_resources["satchel"])
        self.assertNotIn("class_reaction_used_round", rogue.bond_flags)
        self.assertFalse(any(key.startswith("rogue_mark") for key in target.bond_flags))
        self.assertFalse(any(key.startswith("rogue_poison") for key in target.bond_flags))

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

    def test_warrior_class_gets_base_grit_and_combat_actions(self) -> None:
        game, warrior = build_game_with_player(
            "Warrior",
            {"STR": 15, "DEX": 12, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        enemy = create_enemy("bandit")
        encounter = Encounter("Sparring", "A quick pressure test.", [enemy])

        game.prepare_warrior_grit_for_combat(warrior)

        self.assertEqual(warrior.resources["grit"], 1)
        self.assertEqual(warrior.max_resources["grit"], 6)
        options = game.get_player_combat_options(warrior, encounter, heroes=[warrior])
        self.assertIn("Take Guard Stance", options)
        self.assertIn("Shove", options)
        self.assertIn("Weapon Read", options)

    def test_warrior_guard_stance_uses_buffed_defense_avoidance_and_stability(self) -> None:
        game, warrior = build_game_with_player(
            "Warrior",
            {"STR": 15, "DEX": 12, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )

        self.assertEqual(game.effective_defense_percent(warrior, damage_type="slashing"), 40)
        self.assertEqual(game.effective_avoidance(warrior), 0)
        self.assertEqual(game.effective_stability(warrior), 3)

        game.use_guard_stance(warrior)

        self.assertEqual(game.effective_defense_percent(warrior, damage_type="slashing"), 60)
        self.assertEqual(game.effective_avoidance(warrior), 1)
        self.assertEqual(game.effective_stability(warrior), 5)
        self.assertEqual(game.status_value(warrior, "attack_penalty"), 2)

    def test_warrior_gains_grit_from_wounds_and_glances_during_combat(self) -> None:
        game, warrior = build_game_with_player(
            "Warrior",
            {"STR": 15, "DEX": 12, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        game.prepare_warrior_grit_for_combat(warrior)

        game.apply_damage(warrior, 10, damage_type="slashing", apply_defense=True)
        self.assertEqual(warrior.resources["grit"], 1)

        game._in_combat = True
        game.apply_damage(warrior, 10, damage_type="slashing", apply_defense=True)
        self.assertEqual(warrior.resources["grit"], 2)

        game.apply_damage(warrior, 1, damage_type="slashing", apply_defense=True)
        self.assertTrue(game.last_damage_was_glance())
        self.assertEqual(warrior.resources["grit"], 3)

    def test_warrior_shove_targets_stability_and_grants_grit_on_strong_shove(self) -> None:
        game, warrior = build_game_with_player(
            "Warrior",
            {"STR": 15, "DEX": 12, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        enemy = create_enemy("bandit")
        game.prepare_warrior_grit_for_combat(warrior)
        game._in_combat = True
        game.roll_check_d20 = lambda *args, **kwargs: D20Outcome(kept=20, rolls=[20], rerolls=[], advantage_state=0)  # type: ignore[method-assign]

        game.use_warrior_shove(warrior, enemy)

        self.assertTrue(game.has_status(enemy, "prone"))
        self.assertTrue(game.has_status(enemy, "reeling"))
        self.assertEqual(warrior.resources["grit"], 2)

    def test_weapon_read_reports_defense_avoidance_and_stability(self) -> None:
        log: list[str] = []
        game, warrior = build_game_with_player(
            "Warrior",
            {"STR": 15, "DEX": 12, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
        )
        game.output_fn = log.append
        enemy = create_enemy("animated_armor")

        game.use_weapon_read(warrior, enemy)

        rendered = "\n".join(log)
        self.assertIn("Weapon Read:", rendered)
        self.assertIn("Defense", rendered)
        self.assertIn("Avoidance", rendered)
        self.assertIn("Stability", rendered)
        self.assertIn("Best answer:", rendered)


if __name__ == "__main__":
    unittest.main()
