# Aethrune Combat Randomness Tuning Plan V1

Current combat has healthy average damage in several checked encounters, but the turn-to-turn spread is wide. A correct action can produce a blank turn, then the next seed can land a critical hit, win initiative, and delete a target before the player has had time to read the fight. The tuning work should make good choices produce steadier pressure while keeping dice visible enough to feel alive.

This plan sits beside:

- `information/Retcon story/Systems/aethrune_combat_redesign_v1.md`
- `information/Retcon story/Systems/aethrune_combat_balance_current_levels_v1.md`

## Test Snapshot

Tests run before drafting:

```text
py -3 -m pytest tests\test_combat_resolver.py
112 passed

py -3 -m pytest tests\test_full_encounter_pass.py
6 passed
```

Arcane Bolt cooldown was then reduced by one turn in code and simulator math. Post-change verification:

```text
py -3 -m pytest tests\test_combat_resolver.py
112 passed

py -3 -m pytest tests\test_full_encounter_pass.py
6 passed
```

Current variance probe after the cooldown change:

| Probe | Target | Accuracy | Defense or cycle | Mean | SD | CV | P10 / P50 / P90 | Zero result | Max |
| --- | ---: | ---: | --- | ---: | ---: | ---: | --- | ---: | ---: |
| L1 Warrior weapon vs `bandit` | `8` | `+5` | `10%` Defense | `5.94` | `2.98` | `0.50` | `0 / 6 / 9` | `10.0%` | `17` |
| L1 Warrior weapon vs `false_map_skirmisher` | `11` | `+5` | `15%` Defense | `4.60` | `3.26` | `0.71` | `0 / 5 / 9` | `25.0%` | `16` |
| L1 Warrior weapon vs `animated_armor` | `7` | `+5` | `45%` Defense | `3.57` | `1.64` | `0.46` | `2 / 3 / 6` | `5.0%` | `10` |
| L1 Mage Arcane Bolt bonus cycle | `8` | `+5` | `2` turn cycle | `2.54` | `2.93` | `1.16` | `0 / 0 / 7` | `55.0%` | `11` |
| L1 Mage Arcane Bolt action cycle | `8` | `+5` | `2` turn cycle | `5.08` | `5.87` | `1.16` | `0 / 0 / 14` | `55.0%` | `22` |

Encounter-pass probe after the cooldown change:

| Encounter | Party DPR | Enemy DPR | Rounds to clear | Rounds to defeat | Survival margin |
| --- | ---: | ---: | ---: | ---: | ---: |
| Basic raiders | `27.41` | `9.71` | `1.28` | `11.44` | `10.16` |
| High Defense brutes | `19.34` | `13.97` | `3.72` | `7.94` | `4.22` |
| Sereth group | `27.41` | `11.43` | `2.15` | `9.71` | `7.56` |

Read:

- Average encounter math is passable in the deterministic harness.
- Felt swing comes from zero-result turns, critical spikes, initiative alpha, cooldown gaps, and random focus fire.
- High-Avoidance targets already push a level 1 trained attacker to a `25%` zero-result rate.
- Arcane Bolt now has a shorter two-turn cycle, but the per-turn profile still has `55%` zero results because cooldown and attack miss both produce empty turns.

## Tuning Goal

Combat should keep uncertainty while shrinking the distance between a bad seed and a good seed.

Player-facing targets:

- A strong tactical choice should usually create damage, setup, protection, resource gain, or positional pressure.
- Ordinary fights should have a narrow expected length band. A standard route fight should rarely swing from effortless clear to sudden party collapse.
- Enemy spikes should be readable before they land. A huge hit can happen when the enemy has telegraphed the tool, spent a setup turn, or exposed a counterplay lane.
- Empty turns should have a reason the player can act on: high Avoidance, Ward, Guard, cover, spell resistance, or a named defensive trait.
- Class resources should soften bad streaks. A miss can still build Focus, Edge, Grit, Arc, Toxin, Momentum, Flow, or a target mark.

Suggested quantitative targets:

| Metric | Ordinary fight target | Elite or boss target |
| --- | ---: | ---: |
| Common player attack zero-result chance | `<= 15%` | `<= 25%` before setup, `<= 15%` after setup |
| Common enemy attack zero-result chance | `15%` to `35%` by defender type | `10%` to `30%` |
| Action damage CV | `<= 0.55` for bread-and-butter attacks | `<= 0.75` for burst tools |
| P90 damage vs P50 damage | `<= 1.8x` | `<= 2.3x` for named burst |
| Ordinary enemy single-hit cap vs same-level full-health hero | `35%` of max HP | `45%`, or higher with telegraph |
| Encounter rounds P90 minus P10 | `<= 2` rounds | `<= 3` rounds |
| Standard encounter p90 downed party members | `0` to `1` | `1` to `2` |

## Randomness Sources

### D20 Hit Gate

The attack roll creates the largest damage cliff. A one-point miss deals `0`, while a natural 20 jumps into doubled dice and riders. That cliff feels sharp in low-level fights because each action is a large share of the round.

Current pressure points:

- L1 Warrior vs `false_map_skirmisher`: `25%` zero-result rate.
- D20 roll also decides many rider gates: Sneak Attack delivery, Wound-only poison, Armor Break delivery, Pattern Charge, and downed-state pressure.
- Advantage and disadvantage can turn a fight quickly because they alter both miss rate and critical rate.

### Damage Dice

Low-level damage dice have high relative spread. A `1d8+3` attack can land near its floor or its ceiling, then the critical path doubles dice and widens the top.

Current pressure points:

- L1 Warrior vs `bandit`: median `6`, P90 `9`, max `17`.
- L1 Warrior vs `animated_armor`: heavy Defense compresses routine damage, which is good, but critical hits still create a visible jump.

### Cooldowns And Resource Gaps

Cooldowns create a cadence gap. Arcane Bolt now cycles every two turns, which raises average output and makes the ability available sooner. The ability still has a high per-turn zero-result rate because cooldown and attack rolls can both create an empty turn.

Current pressure points:

- L1 Arcane Bolt bonus cycle: `55%` zero result across the two-turn cadence.
- L1 Arcane Bolt action cycle: max `22`, median `0` across the cadence.

### Initiative Alpha

Initiative uses a full d20 roll. In small fights, an early action can remove a combatant before that side has acted. A seed with two enemies acting before the wounded caster can feel much harsher than the average encounter math predicts.

### Enemy Target Selection

Most enemy archetypes now have target logic, but fallback targeting still uses `rng.choice(conscious_heroes)`. Random focus fire can stack attacks onto a low-HP actor without a readable reason.

Current code locations:

- `dnd_game/gameplay/combat_flow.py`: enemy fallback target choice.
- `dnd_game/gameplay/map_system.py`: some map events choose random hero or enemy targets.

### Saves And Control

Save-driven effects can produce full denial on failure and no visible consequence on success. A one-round control effect matters because one lost turn is a large slice of a short fight.

## Design Principles

- Every hostile action should produce an outcome category: Miss, Pressure, Glance, Wound, Critical, Resist, or Blocked.
- A low roll should often create setup pressure. Damage can fail while the turn still changes the fight.
- Damage spikes should carry setup, cost, exposure, or telegraph text.
- Player-facing smoothing should be stronger than enemy-facing smoothing at levels `1-2`.
- Combat text should show why the result happened and what lever answers it.
- Randomness should decide texture and timing more often than total fight viability.

## Workstream A: Measurement Harness

Add a combat variance harness before large rule changes.

New files:

- `tests/test_combat_variance.py`
- `tools/combat_variance_report.py`

Suggested data models:

```python
@dataclass(frozen=True, slots=True)
class ActionVarianceProfile:
    name: str
    mean: float
    standard_deviation: float
    coefficient_of_variation: float
    zero_result_chance: float
    p10: int
    p50: int
    p90: int
    max_result: int
    critical_chance: float
    critical_damage_share: float


@dataclass(frozen=True, slots=True)
class EncounterVarianceProfile:
    name: str
    seeds: int
    victory_rate: float
    rounds_p10: int
    rounds_p50: int
    rounds_p90: int
    party_hp_p10: int
    party_hp_p50: int
    party_hp_p90: int
    downed_count_p90: int
```

Action probes:

- L1 Warrior vs `bandit`, `false_map_skirmisher`, `animated_armor`
- L1 Mage Minor Channel and Arcane Bolt against `bandit`
- L1 Rogue weapon attack with and without Sneak Attack
- L4 mixed party actions against `ash_brand_enforcer`, `sereth_vane`, `pact_archive_warden`
- Enemy attacks against Warrior, Rogue, Mage at levels `1`, `2`, and `4`

Encounter probes:

- Opening tutorial combat
- Road ambush
- Basic raiders
- Shieldhands
- High-Avoidance scouts
- High-Defense brutes
- Sereth-style named enemy
- A two-wave route chain with one short rest available

Report output:

```text
Action                  Mean  CV    Zero  P10  P50  P90  Max  CritShare
Warrior vs bandit       5.94  .50   10%   0    6    9    17   ...
Warrior vs skirmisher   4.60  .71   25%   0    5    9    16   ...
```

Acceptance tests:

- Ordinary player attacks stay below target zero-result and CV thresholds.
- Elite defensive profiles can exceed ordinary thresholds before setup.
- Setup tools must visibly improve the profile: Pattern Read, Marked, Armor Break, Guard, Ground, Press, Aim.
- Encounter P90 should avoid party collapse in standard fights unless the fight is tagged as boss, trap, or attrition.

## Workstream B: Hit Resolution Smoothing

Add a pressure tier between clean miss and Wound.

Candidate rule:

```text
Attack total below target by 1-3: Pressure.
Attack total below target by 4 or more: Miss.
Natural 1: Miss and no pressure.
Natural 20: Critical, subject to crit smoothing rules.
```

Pressure can do one of these by action type:

| Action type | Pressure result |
| --- | --- |
| Weapon attack | target gains `pressed` until next allied attack, `+1` Accuracy against that target |
| Heavy weapon | target gains `rattled_guard`, next physical hit ignores `5` percentage points of Defense |
| Light weapon | attacker gains `edge` or `focus` once per round |
| Ranged attack | target loses cover or gains `marked` for `1` round |
| Arcane Bolt | attacker gains `1` Pattern Charge or cooldown is shortened by `1` |
| Poison delivery | poison coating is preserved and target gains `exposed_vein` until the next poison attempt |

Caps:

- Pressure Accuracy bonus caps at `+2`.
- Pressure Armor Break caps at `10` percentage points.
- A single actor can gain a miss-compensation resource once per round.
- Enemies can use Pressure, but player attacks should get first tuning pass.

Tests:

- A near miss applies the expected pressure status.
- A clean miss applies no pressure.
- Natural 1 applies no pressure.
- Pressure status expires after the next relevant attack.
- Pressure lowers zero-result rate in the variance harness without raising average DPR above target.

## Workstream C: Bad-Streak Protection

Add a small, visible correction when a player repeatedly fails hostile actions.

Candidate rule:

```text
If a party member ends a hostile action with no Wound, no Glance, and no Pressure,
they gain Bad Streak +1.
Their next hostile action gains +1 Accuracy per Bad Streak, cap +2.
The counter clears when they cause Wound, Glance, Pressure, or a save-based partial effect.
```

Class-specific versions can feel better than a generic hidden buff:

| Class lane | Bad-streak reward |
| --- | --- |
| Warrior | `+1` Grit or `+1` Momentum, once per round |
| Mage | `+1` Focus or Pattern Charge if targeting the same enemy |
| Rogue | `+1` Edge or preserves poison setup |

Player text:

```text
Vale reads the miss and tightens the next line. Accuracy +1.
```

Tests:

- Counter increments only after a true empty hostile action.
- Counter caps at `2`.
- Counter clears on Wound, Glance, Pressure, or save partial.
- Enemy bad-streak protection is disabled for ordinary enemies at levels `1-2`.

## Workstream D: Damage Dice Smoothing

Shift routine damage away from large single dice.

Enemy damage conversion targets:

| Current feel | Smoother expression | Reason |
| --- | --- | --- |
| `1d8+2` ordinary strike | `1d4+4` | Same middle, lower ceiling |
| `1d10+2` brute strike | `2d4+3` | Keeps heft, narrows spread |
| `2d6+2` elite hit | `2d4+4` | Lowers max, raises floor |
| `1d12+3` telegraphed blow | keep, add wind-up | Spike remains readable |

Player damage conversion can wait until enemy spikes are tamed. Player burst feels good when it is earned and explained.

Low-level enemy limits:

- Level `1` ordinary enemies should use no larger than `1d6+2` unless the attack is telegraphed.
- Level `1` brutes can reach `1d8+2`, with low Accuracy or a setup cue.
- Level `2` ordinary enemies can use `1d6+3` or `2d4+1`.
- Multiattack enemies should split targets by default unless they have a hunter, marked, or executioner tag.

Tests:

- Enemy action profile CV stays below `0.55` for ordinary attacks.
- Enemy P90 damage against same-level heroes stays under the spike cap.
- Boss and elite exceptions must be tagged in data or archetype logic.

## Workstream E: Critical Hit Tuning

Critical hits should feel sharp without turning one d20 into a full fight result.

Candidate rules:

| Source | Critical damage rule |
| --- | --- |
| Player weapon | current doubled dice during first pass |
| Ordinary enemy | normal dice plus one max weapon die |
| Elite enemy | doubled dice, then apply spike cap |
| Boss telegraphed attack | doubled dice or special expression, no cap if wind-up was shown |
| Arcane Bolt | doubled dice remains acceptable because cooldown and MP cost gate it |

Enemy spike cap:

```text
Ordinary enemy critical cannot deal more than 35% of the target's max HP.
Elite enemy critical cannot deal more than 45% of the target's max HP.
Boss critical can exceed the cap only when the attack has telegraph text or a setup status.
```

Cap text:

```text
The blow nearly folds Mira, but the wardline catches the worst of it.
```

Tests:

- Ordinary enemy crits obey cap against Warrior, Rogue, and Mage at levels `1-4`.
- Player crits keep current damage in the first pass.
- Boss flagged attacks bypass or raise cap only when tagged.
- Critical hit profile P90 and max fall inside target thresholds.

## Workstream F: Glance And Armor Pressure

Glances already explain armor doing work. Use them to reduce empty-turn feel against high Defense targets.

Candidate rule:

```text
When a physical hit becomes a Glance through Defense, Ward, Guard, or temporary HP,
apply one stack of `chipped` to the target.
The next physical Wound against that target gains +1 damage or ignores 5 Defense percentage points.
Stacks cap at 2 and expire at round end.
```

Class hooks:

| Class lane | Glance hook |
| --- | --- |
| Juggernaut | gains Momentum from own Glances and enemy Glances against Guard |
| Weapon Master | `chipped` can become Armor Break through `Dent The Shell` |
| Bloodreaver | marked enemy Glance grants Blood Debt only once per round |
| Poisoner | Glance preserves poison and applies `opened_armor` for the next poison attempt |

Tests:

- Glance applies `chipped` on eligible physical hits.
- Ward-only absorption can apply pressure only if the hit connected.
- `chipped` cap and expiry work.
- High-Defense brute encounter P90 rounds narrows after the rule.

## Workstream G: Enemy Targeting

Replace fallback random target choice with weighted tactical scoring.

Current fallback:

```python
target = marked_target or self.rng.choice(conscious_heroes)
```

Proposed helper:

```python
def enemy_target_score(enemy, hero, *, marked_target, previous_targets, round_number) -> tuple[int, int, int, int]:
    return (
        marked_bonus,
        threat_bonus,
        vulnerability_bonus,
        anti_focus_penalty,
    )
```

Scoring table:

| Factor | Score |
| --- | ---: |
| Hero is Marked | `+8` |
| Enemy has hunter or executioner tag and hero is below 40% HP | `+5` |
| Hero is concentrating, channeling, or has high attack bonus | `+3` |
| Hero is guarding an ally | `+2` |
| Hero was targeted by this enemy last turn | `-3` |
| Hero was targeted by two enemies this round | `-6` |
| Hero is downed | avoid unless enemy has executioner tag |

Randomness stays as tie-breaker:

```python
top_score = max(scores)
candidates = [hero for hero, score in scores if score == top_score]
target = self.rng.choice(candidates)
```

Enemy personality exceptions:

| Tag | Behavior |
| --- | --- |
| `hunter` | can focus wounded targets |
| `executioner` | can strike downed targets in boss or horror scenes |
| `beast` | prefers nearest or bloodied target |
| `disciplined` | follows marked and commander logic |
| `panicked` | uses random target choice |
| `mindless` | attacks nearest or last source of damage |

Tests:

- Fallback target selection avoids random focus fire in ordinary fights.
- Marked target still matters.
- Hunter and executioner tags can focus fire.
- Targeting remains deterministic under fixed seeds.

## Workstream H: Initiative And Round Flow

Reduce alpha-strike swings from initiative.

Candidate options:

1. Keep current d20 initiative, add encounter safeguards.
2. Use side initiative for ordinary fights, then alternate actors by side.
3. Use individual initiative for bosses and ambush scenes.
4. Add a round-one protection rule for fragile party members at levels `1-2`.

Recommended first pass:

```text
Keep current initiative.
Add anti-focus targeting.
Add enemy spike caps.
Add round-one telegraph rules for brute and control openers.
```

If variance remains high, move to alternating side slots:

```text
Highest initiative actor acts first.
Then sides alternate: hero, enemy, hero, enemy.
Within a side, use initiative order.
Bosses can reserve one reaction or lair move outside the alternation.
```

Tests:

- Initiative order remains stable under fixed seeds.
- Alternating mode, if enabled, reduces P90 downed count in level `1` encounters.
- Boss scenes can opt out through encounter metadata.

## Workstream I: Save And Control Smoothing

Turn all-or-empty control into degrees.

Candidate save degree table:

| Save result | Outcome |
| --- | --- |
| Fail by `5+` | full damage or full status duration |
| Fail by `1-4` | half duration, soft status, or reduced damage |
| Success by `0-4` | no hard status, small pressure or half damage |
| Success by `5+` | clear resist, possible counter text for trained classes |

Control examples:

| Effect | Full fail | Close fail | Success |
| --- | --- | --- | --- |
| Blinding shot | `blinded` 1 round | `reeling` 1 round | no status |
| Weighted snare | `restrained` 2 rounds | `slowed` or `reeling` 1 round | no status |
| Charm pressure | `charmed` 1 round | cannot target caster this turn | no status |
| Fear pulse | loses action or flees | `shaken`, `-1` Accuracy | no status |

Tests:

- Close failures produce reduced status.
- Strong failures preserve threat.
- Success avoids hard denial.
- Existing boss and named scenes can opt into harsher outcomes with tags.

## Workstream J: Arcane Bolt Follow-Up

Completed change:

- Cooldown duration changed from `3` to `2`.
- Simulator cooldown cycle changed from `3` to `2`.
- Resource spending projections now use one Arcane Bolt per two simulated rounds.

Follow-up options if Arcane Bolt still feels bumpy:

| Option | Effect |
| --- | --- |
| Miss shortens cooldown | A miss sets cooldown to `1` after the current turn tick |
| Miss grants Pattern Charge | The bolt misses damage but advances Arcanist setup |
| Action cast cannot fully whiff | Action Arcane Bolt deals `1` force pressure on miss by `1-3` |
| Cooldown as charge meter | Cast every turn at base damage; every other turn becomes charged |
| MP partial refund | A clean miss refunds `1` MP once per round |

Recommended next step:

```text
Use Pressure for near misses first.
If Arcane Bolt still has too many blank turns, add Pattern Charge on miss.
```

Tests:

- Arcane Bolt cooldown remains `2`.
- Action and bonus versions share cooldown.
- Simulator expected DPR reflects the two-turn cycle.
- Miss-pressure behavior updates variance profiles.

## Workstream K: Encounter And Enemy Data Pass

After mechanics smoothing, retune enemy data.

Audit fields:

- `weapon.damage`
- `weapon.damage_bonus`
- `attack_bonus`
- `bond_flags["combat_profile"]["avoidance"]`
- `bond_flags["combat_profile"]["defense_percent"]`
- `resources` that drive one-shot abilities
- targeting archetype code in `combat_flow.py`

Enemy groups to review:

| Group | Risk | Tuning move |
| --- | --- | --- |
| Low-level archers | focus fire from safety | anti-focus targeting, lower spike dice |
| Brutes | high single-hit damage | smoother dice, telegraphed smash |
| Shieldhands | slow, glancing fights | Glance pressure and Armor Break lanes |
| High-Avoidance scouts | repeated blank turns | Pressure on near miss, lower Avoidance if needed |
| Control casters | failed save can erase turn | degree table |
| Named enemies | seed-dependent difficulty | telegraphs, caps, encounter-specific variance tests |

Data-pass target:

- Ordinary level `1` enemy max single-hit damage should usually land below `8`.
- Ordinary level `2` enemy max single-hit damage should usually land below `10`.
- Elite enemies can exceed this with tags and telegraph text.
- Boss burst should appear in examine text or pre-attack narration.

## Implementation Sequence

1. Add `tests/test_combat_variance.py` and `tools/combat_variance_report.py`.
2. Record current action profiles and encounter profiles as baseline snapshots.
3. Add Pressure outcome for near misses.
4. Add player bad-streak protection through class-flavored resources.
5. Add enemy target scoring and anti-focus penalties.
6. Smooth ordinary enemy damage dice at levels `1-2`.
7. Add enemy critical spike caps.
8. Add Glance pressure for high-Defense fights.
9. Add save degrees for common player-targeting control effects.
10. Re-run variance report and update `aethrune_combat_balance_current_levels_v1.md`.
11. Sync Android port after desktop combat tests pass.

Suggested branch order:

| Branch | Scope | Exit check |
| --- | --- | --- |
| `codex/combat-variance-harness` | measurements only | report generated, no behavior change |
| `codex/combat-pressure-tier` | near miss and miss-resource hooks | action CV and zero-result tests pass |
| `codex/combat-targeting-smoothing` | enemy target scoring | p90 downed count improves |
| `codex/combat-damage-smoothing` | enemy dice and crit caps | spike caps pass |
| `codex/combat-control-degrees` | save degree table | control tests pass |

## Acceptance Checklist

- Combat resolver tests pass.
- Full encounter pass tests pass.
- New variance tests pass with fixed seeds.
- Android port mirrors desktop combat code.
- Basic raiders, shieldhands, high-Avoidance scouts, high-Defense brutes, and Sereth-style group all have variance reports.
- Player attacks have fewer blank turns in ordinary fights.
- Enemy focus fire has readable reasons.
- Ordinary enemy crits cannot erase a same-level full-health hero.
- Boss exceptions are tagged and tested.
- Combat text uses Miss, Pressure, Glance, Wound, Critical, and Resist language consistently.

## First Patch Recommendation

Start with measurement, Pressure, and target scoring.

That order gives the quickest confidence:

1. Measurement shows where outcomes are swinging.
2. Pressure reduces blank turns without rewriting every weapon and spell.
3. Target scoring reduces sudden party collapse from random focus fire.

Damage dice and crit caps should follow once the harness can show before-and-after spread.
