from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product
import re


_DICE_RE = re.compile(r"\s*(?P<count>\d*)d(?P<sides>\d+)(?P<modifier>[+-]\d+)?\s*")


@dataclass(frozen=True, slots=True)
class AttackRollSimulation:
    target_number: int
    accuracy_bonus: int
    required_roll: int
    advantage_state: int
    miss_chance: float
    normal_hit_chance: float
    critical_chance: float

    @property
    def hit_chance(self) -> float:
        return self.normal_hit_chance + self.critical_chance


@dataclass(frozen=True, slots=True)
class DamageSimulation:
    defense_percent: int
    armor_break_percent: int
    expected_hp_damage_on_normal_hit: float
    expected_hp_damage_on_critical_hit: float
    glance_chance_on_normal_hit: float
    glance_chance_on_critical_hit: float
    wound_chance_on_normal_hit: float
    wound_chance_on_critical_hit: float


@dataclass(frozen=True, slots=True)
class WeaponAttackSimulation:
    attack_roll: AttackRollSimulation
    damage: DamageSimulation

    @property
    def target_number(self) -> int:
        return self.attack_roll.target_number

    @property
    def accuracy_bonus(self) -> int:
        return self.attack_roll.accuracy_bonus

    @property
    def hit_chance(self) -> float:
        return self.attack_roll.hit_chance

    @property
    def miss_chance(self) -> float:
        return self.attack_roll.miss_chance

    @property
    def normal_hit_chance(self) -> float:
        return self.attack_roll.normal_hit_chance

    @property
    def critical_chance(self) -> float:
        return self.attack_roll.critical_chance

    @property
    def expected_hp_damage(self) -> float:
        return (
            self.normal_hit_chance * self.damage.expected_hp_damage_on_normal_hit
            + self.critical_chance * self.damage.expected_hp_damage_on_critical_hit
        )

    @property
    def glance_chance(self) -> float:
        return (
            self.normal_hit_chance * self.damage.glance_chance_on_normal_hit
            + self.critical_chance * self.damage.glance_chance_on_critical_hit
        )

    @property
    def wound_chance(self) -> float:
        return (
            self.normal_hit_chance * self.damage.wound_chance_on_normal_hit
            + self.critical_chance * self.damage.wound_chance_on_critical_hit
        )


def d20_kept_distribution(*, advantage_state: int = 0, lucky: bool = False) -> dict[int, float]:
    roll_count = 2 if advantage_state else 1
    totals: dict[int, float] = defaultdict(float)
    raw_weight = 1 / (20**roll_count)
    for raw_rolls in product(range(1, 21), repeat=roll_count):
        processed_options: list[list[tuple[int, float]]] = []
        for raw in raw_rolls:
            if lucky and raw == 1:
                processed_options.append([(reroll, 1 / 20) for reroll in range(1, 21)])
            else:
                processed_options.append([(raw, 1.0)])
        for processed_rolls in product(*processed_options):
            rolls = [value for value, _ in processed_rolls]
            chance = raw_weight
            for _, option_weight in processed_rolls:
                chance *= option_weight
            if advantage_state > 0:
                kept = max(rolls)
            elif advantage_state < 0:
                kept = min(rolls)
            else:
                kept = rolls[0]
            totals[kept] += chance
    return dict(totals)


def simulate_attack_roll(
    *,
    target_number: int,
    accuracy_bonus: int,
    advantage_state: int = 0,
    critical_threshold: int = 20,
    lucky: bool = False,
    critical_immunity: bool = False,
) -> AttackRollSimulation:
    miss = 0.0
    normal = 0.0
    critical = 0.0
    for kept, chance in d20_kept_distribution(advantage_state=advantage_state, lucky=lucky).items():
        if kept == 1:
            miss += chance
            continue
        is_critical = kept >= critical_threshold and not critical_immunity
        if is_critical:
            critical += chance
            continue
        if kept + accuracy_bonus < target_number:
            miss += chance
        else:
            normal += chance
    required_roll = max(2, min(20, target_number - accuracy_bonus))
    return AttackRollSimulation(
        target_number=target_number,
        accuracy_bonus=accuracy_bonus,
        required_roll=required_roll,
        advantage_state=advantage_state,
        miss_chance=miss,
        normal_hit_chance=normal,
        critical_chance=critical,
    )


def dice_total_distribution(expression: str, *, critical: bool = False) -> dict[int, float]:
    match = _DICE_RE.fullmatch(expression)
    if match is None:
        raise ValueError(f"Unsupported dice expression: {expression}")
    count = int(match.group("count") or "1")
    sides = int(match.group("sides"))
    modifier = int(match.group("modifier") or "0")
    if critical:
        count *= 2
    totals: dict[int, int] = {0: 1}
    for _ in range(count):
        next_totals: dict[int, int] = defaultdict(int)
        for subtotal, ways in totals.items():
            for face in range(1, sides + 1):
                next_totals[subtotal + face] += ways
        totals = dict(next_totals)
    total_ways = sides**count
    return {total + modifier: ways / total_ways for total, ways in totals.items()}


def _resisted_damage(game, target, damage: int, damage_type: str) -> int:
    resisted = False
    if game.has_status(target, "petrified"):
        damage //= 2
    if damage_type == "poison" and "dwarven_resilience" in target.features:
        resisted = True
    if damage_type == "fire" and "hellish_resistance" in target.features:
        resisted = True
    if game.has_damage_resistance(target, damage_type):
        resisted = True
    if resisted:
        damage //= 2
    return damage


def simulate_damage_after_defense(
    game,
    target,
    damage_distribution: dict[int, float],
    *,
    damage_type: str = "",
    defense_percent: int = 0,
    apply_defense: bool = True,
    minimum_raw_damage: int = 1,
) -> tuple[float, float, float]:
    expected_hp_damage = 0.0
    glance_chance = 0.0
    wound_chance = 0.0
    for raw_total, chance in damage_distribution.items():
        raw_damage = max(minimum_raw_damage, raw_total)
        resisted_damage = _resisted_damage(game, target, raw_damage, damage_type)
        mitigated_damage = resisted_damage
        if apply_defense and game.damage_type_uses_defense(damage_type):
            mitigated_damage = mitigated_damage * (100 - defense_percent) // 100
        hp_damage = max(0, mitigated_damage)
        expected_hp_damage += hp_damage * chance
        if apply_defense and raw_damage > 0 and resisted_damage > 0 and mitigated_damage <= 0:
            glance_chance += chance
        if hp_damage > 0:
            wound_chance += chance
    return expected_hp_damage, glance_chance, wound_chance


def simulate_weapon_damage(
    game,
    attacker,
    target,
    *,
    damage_type: str = "",
    armor_break_percent: int = 0,
    armor_break: int = 0,
) -> DamageSimulation:
    total_armor_break = game.total_armor_break_percent(
        target,
        source_actor=attacker,
        incoming_percent=armor_break_percent,
        incoming_steps=armor_break,
    )
    defense_percent = game.effective_defense_percent(
        target,
        damage_type=damage_type,
        armor_break_percent=total_armor_break,
    )
    damage_bonus = attacker.damage_bonus() + game.status_damage_modifier(attacker)
    normal_distribution = {
        total + damage_bonus: chance for total, chance in dice_total_distribution(attacker.weapon.damage).items()
    }
    critical_distribution = {
        total + damage_bonus: chance
        for total, chance in dice_total_distribution(attacker.weapon.damage, critical=True).items()
    }
    normal_expected, normal_glance, normal_wound = simulate_damage_after_defense(
        game,
        target,
        normal_distribution,
        damage_type=damage_type,
        defense_percent=defense_percent,
    )
    critical_expected, critical_glance, critical_wound = simulate_damage_after_defense(
        game,
        target,
        critical_distribution,
        damage_type=damage_type,
        defense_percent=defense_percent,
    )
    return DamageSimulation(
        defense_percent=defense_percent,
        armor_break_percent=total_armor_break,
        expected_hp_damage_on_normal_hit=normal_expected,
        expected_hp_damage_on_critical_hit=critical_expected,
        glance_chance_on_normal_hit=normal_glance,
        glance_chance_on_critical_hit=critical_glance,
        wound_chance_on_normal_hit=normal_wound,
        wound_chance_on_critical_hit=critical_wound,
    )


def simulate_weapon_attack(
    game,
    attacker,
    target,
    *,
    heroes: list | None = None,
    enemies: list | None = None,
    dodging: set[str] | frozenset[str] | None = None,
    advantage_state: int | None = None,
    damage_type: str | None = None,
    armor_break_percent: int = 0,
    armor_break: int = 0,
) -> WeaponAttackSimulation:
    heroes = heroes if heroes is not None else [attacker]
    enemies = enemies if enemies is not None else []
    dodging = dodging if dodging is not None else frozenset()
    if advantage_state is None:
        advantage_state = game.attack_advantage_state(
            attacker,
            target,
            heroes,
            enemies,
            dodging,
            ranged=attacker.weapon.ranged,
        )
    target_number = game.effective_attack_target_number(target)
    accuracy_bonus = (
        attacker.attack_bonus()
        + game.ally_pressure_bonus(attacker, heroes, ranged=attacker.weapon.ranged)
        + game.status_accuracy_modifier(attacker)
    )
    critical_threshold = game.critical_threshold(attacker) if hasattr(game, "critical_threshold") else 20
    attack_roll = simulate_attack_roll(
        target_number=target_number,
        accuracy_bonus=accuracy_bonus,
        advantage_state=advantage_state,
        critical_threshold=critical_threshold,
        lucky="lucky" in getattr(attacker, "features", []),
        critical_immunity=bool(getattr(target, "gear_bonuses", {}).get("crit_immunity", 0)),
    )
    weapon_item = game.equipped_weapon_item(attacker)
    resolved_damage_type = damage_type
    if resolved_damage_type is None:
        resolved_damage_type = weapon_item.damage_type if weapon_item is not None else ""
    damage = simulate_weapon_damage(
        game,
        attacker,
        target,
        damage_type=resolved_damage_type or "",
        armor_break_percent=armor_break_percent,
        armor_break=armor_break,
    )
    return WeaponAttackSimulation(attack_roll=attack_roll, damage=damage)
