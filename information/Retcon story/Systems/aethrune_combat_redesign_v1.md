# Aethrune Combat Redesign V1

Current level-scale tuning and simulation results live in `information/Retcon story/Systems/aethrune_combat_balance_current_levels_v1.md`.

## Purpose

This draft gives armor and Defense a clearer job. Defense is percentage damage reduction after a physical hit lands. Hit chance comes from the attacker's Accuracy against the defender's Avoidance, which is built from Agility, awareness, cover, stance, and conditions. Spell effects that already use saving throws can keep that lane during migration.

The goal is a text-combat system where a mailed warrior feels different from a quick duelist. A hammer blow can land against plate and lose half its force. A knife can miss a moving target by a finger's width. A flame channel can force a resist check without caring how thick the breastplate is.

## Design Commitments

- Armor reduces damage by percentage. Agility prevents contact.
- A hit can land, lose force through armor, and still create a Wound.
- A hit can become a Glance when percentage Defense, Ward, Guard, or temporary HP leaves no HP damage.
- Spell saves remain a stable lane for channels, hazards, fear, poison, and signal pressure.
- The text UI explains why a result happened: miss, Glance, Wound, Resist Check, Ward, Defense, or condition.
- Every class role gets a hook in the new math. Warriors care about Defense and Glances, Mages care about Resist Checks and fields, Rogues care about Avoidance and exposed targets.

## System Snapshot

Most turns answer four questions.

| Question | System lane |
| --- | --- |
| Did the attack connect? | `d20 + Accuracy` against `10 + Avoidance`. |
| How much force did armor remove? | Physical damage reduced by Defense percentage. |
| Did the target withstand a spell, hazard, poison, or fear effect? | Resist Check against DC. |
| Did the hit create a Wound? | Final HP damage above `0`. Wound riders then apply. |

Default weapon example:

```text
Attack Roll = d20 + Accuracy
Avoid Target = 10 + Avoidance
Hit if Attack Roll >= Avoid Target

Modified Damage = weapon dice + damage bonuses
Effective Defense = clamp(Defense% - Armor Break%, 0%, Defense Cap)
HP Damage = floor(Modified Damage * (100% - Effective Defense))
```

Default spell-save example:

```text
Resist Roll = d20 + save bonus + condition bonuses
Channel DC = 8 + training bonus + casting stat modifier + focus bonuses
```

## Public Combat Sheet

Characters and enemies should show these values in combat summaries.

| Field | Meaning |
| --- | --- |
| HP | Current ability to stay standing. |
| Defense | Percentage physical damage reduction from armor, shield, hide, ward shell, Guard, or stance. |
| Avoidance | Target-side miss pressure from Agility, stance, cover, awareness, and conditions. |
| Accuracy | Main attack connection bonus. Weapons and channels can override it. |
| Stability | Resistance to shove, pull, grapple, knockdown, and forced movement. |
| Saves / Resist Checks | Body, mind, and signal resistance. Uses existing save bonus logic. |
| Ward | Temporary shield layer from Mage, item, or field effects. |
| Stance | Current combat mode such as Guard, Mobile, Brace, Aim, or Aggressive. |
| Tags | Combat-readable traits such as `armored`, `evasive`, `bleeds`, `sealed`, `construct`, `warded`, `flying`, `large`. |

Example display:

```text
Rhogar - HP 34/40 - Defense 40% - Avoidance +0 - Stability +4 - Stance: Guard
Kaelis - HP 22/28 - Defense 10% - Avoidance +5 - Stability +1 - Stance: Mobile - Hidden
Ashen Shieldhand - HP 18/18 - Defense 35% - Avoidance +0 - Stability +3 - Tags: armored, shielded
```

## Legacy Ability Names

The first implementation can keep existing internal ability names while presenting Aethrune-facing labels.

| Current internal ability | Public combat role |
| --- | --- |
| STR | Might: heavy attacks, shove, Stability, Armor Break. |
| DEX | Agility: Avoidance, initiative, finesse attacks, ranged attacks. |
| CON | Endurance: HP, poison, Bleeding, fatigue, backlash. |
| INT | Reason: pattern reads, technical channels, traps. |
| WIS | Instinct: field sense, fear resistance, triage. |
| CHA | Presence: command, taunt, morale, force of will. |

The code can still use existing keys while docs and UI move toward public terms.

## Combat Terms

| Term | Use |
| --- | --- |
| Accuracy | Bonus used to land weapon attacks, thrown attacks, physical spell attacks, and monster strikes. |
| Avoidance | Target-side miss pressure. Built mostly from Agility, awareness, stance, cover, and conditions. |
| Defense | Percentage physical damage reduction. Most armor grants `10%` to `45%` before stance, shield, Guard, and break effects. |
| Defense Cap | Maximum effective Defense. Ordinary cap is `75%`; bosses and special scenes can lower or raise it. |
| Guard | Temporary protection from a stance, shield, ally intercept, or class feature. Guard usually adds Defense percentage and sometimes Avoidance. |
| Stability | Resistance to shoves, knockdowns, forced movement, grapples, and stance breaks. |
| Resist Check | Existing saving throw structure. Keep it for spell effects, poisons, fear, forced movement, and hazards. |
| Armor Break | Temporary percentage-point reduction to Defense. `Armor Break 1` means `-10 percentage points`. |
| Glance | A hit that lands but deals `0` HP damage after Defense, Ward, Guard, and temporary HP. |
| Wound | HP damage after Defense and protection layers. Bleed, poison delivery, and many injury riders need a Wound. |

## Turn Anatomy

Each combatant begins a turn with:

| Resource | Default |
| --- | --- |
| Action | `1` |
| Bonus action | `1` |
| Reaction | `1` per round |
| Movement | abstract lane shift or local reposition |
| Stance choice | maintain current stance or switch if free |

Turn phases:

1. Start-turn conditions tick.
2. Start-turn saves or Resist Checks resolve.
3. Stance can be chosen or maintained.
4. The actor takes actions, bonus actions, item uses, and movement.
5. Reactions from other combatants can trigger.
6. End-turn conditions tick.
7. Temporary "until next turn" modifiers expire.

## Action Menu Groups

The text UI can keep the existing grouped combat menu.

| Group | Examples |
| --- | --- |
| Action | Strike, Channel, Field Mend, Shove, Dirty Trick, Dodge, Help a Downed Ally. |
| Bonus Action | Stance spike, Hide, Quick Mix, Red Mark, Rage, Bardic Inspiration. |
| Reaction | Ward Shell, Intercept, Slip Away, Counterstrike. |
| Item | Drink potion, use vial, throw bomb, apply antidote. |
| Social | Taunt, command, intimidate, plead, expose evidence when scene supports it. |
| Escape | Flee, disengage, create opening, cover retreat. |
| End Turn | pass remaining actions. |

If a character has no meaningful stance choice, the UI can hide stance selection.

## Reactions

A reaction is a once-per-round answer to a trigger.

| Trigger | Possible reactions |
| --- | --- |
| Ally takes a physical hit nearby | Intercept, Guard Ally, Ward Shell. |
| Enemy misses by a narrow margin | Rogue Slip Away, Shadowguard counter. |
| Hostile channel targets an ally | Spellguard Catch Spark or Turn Channel. |
| Enemy leaves engagement | Opportunity strike, pin, trip. |
| Marked target heals, flees, or commands | Assassin interrupt, Poisoner Bad Antidote. |
| Character would drop to `0` HP | Bloodreaver Borrowed Pulse, Aethermancer Borrowed Breath, class last-chance tools. |

Reactions should be prompted only when the player has a useful legal response.

## Initiative And Surprise

Initiative stays familiar.

```text
Initiative = d20 + Agility modifier + initiative bonuses + encounter bonus
```

Tie order:

1. Higher Agility.
2. Higher Instinct if ambush or awareness matters.
3. Heroes before ordinary enemies.
4. Bosses before allied summons.

Surprise:

| State | Effect |
| --- | --- |
| Surprised | loses first action and reaction; can still suffer start-turn effects. |
| Alert | cannot be Surprised by ordinary ambush. |
| Hidden opener | first attack can treat target as exposed. |
| Scout advantage | party can choose starting stance or lane. |

## Positioning Model

The game can stay text-first by using lanes rather than exact grid squares.

| Lane | Meaning |
| --- | --- |
| Engaged | in melee with one or more enemies. |
| Near | can reach with a move, thrown weapon, short channel, or charge. |
| Far | requires ranged attack, long channel, dash, or two moves. |
| Covered | has physical cover against ranged attacks. |
| Elevated | gains line and ranged Accuracy; may risk falling or exposure. |
| Obscured | smoke, darkness, dust, steam, crowd, hanging cloth, or clutter. |
| Hazard | burning oil, frost, acid, unstable floor, sharp debris, or signal field. |

Movement defaults:

| Move | Cost |
| --- | --- |
| Shift within same lane | free once per turn if not Restrained or Grappled. |
| Move Near to Engaged | movement. |
| Move Engaged to Near | movement; may provoke unless Disengage, Mobile, smoke, or class feature. |
| Move Near to Far | action or movement plus cover/route support. |
| Move Far to Near | movement. |
| Enter or leave Hazard | may trigger Resist Check. |

Reach weapons can threaten an adjacent lane. Ranged attacks work best from Near or Far. Melee attacks require Engaged unless a weapon or monster trait says otherwise.

## Hit Resolution

Weapon attacks use a contested target number.

```text
Attack Roll = d20 + Accuracy
Avoid Target = 10 + target Avoidance
Hit if Attack Roll >= Avoid Target
```

Natural results:

| Roll | Result |
| ---: | --- |
| 1 | Miss. |
| 20 | Hit. The attack can become a critical hit. |

Margin results:

| Margin | Result |
| ---: | --- |
| -5 or lower | Clean miss. |
| -4 to -1 | Near miss. Some abilities can trigger from this. |
| 0 to 4 | Hit. |
| 5 to 9 | Strong hit. Some weapons add a rider. |
| 10+ | Critical threat. Confirm as critical if the weapon or ability allows it. |

## Accuracy

Accuracy is the attacker's chance to connect.

```text
Accuracy = attack stat modifier + training bonus + weapon accuracy + feature bonuses + situational modifiers
```

Recommended attack stats:

| Attack type | Stat |
| --- | --- |
| Heavy melee | Might / STR |
| One-handed melee | Might / STR or Agility / DEX if the weapon has finesse |
| Light melee | Agility / DEX |
| Thrown weapons | Might / STR or Agility / DEX by weapon |
| Bows | Agility / DEX |
| Crossbows and firearms, if added | Agility / DEX plus weapon training |
| Beast bites, claws, slams | Might / STR or Instinct by creature |
| Physical spell projectile | Casting stat or Agility by channel design |

Training bonus can start as the current proficiency bonus. Class features, weapon mastery, equipment quality, companion setup, and statuses add to the same channel.

### Accuracy Modifiers

| Factor | Modifier |
| --- | ---: |
| Attacker has Edge / advantage | roll twice, keep higher |
| Attacker has Snag / disadvantage | roll twice, keep lower |
| High ground, clean line, braced aim | `+1` to `+2` |
| Target Marked by an ally | `+1` |
| Flanking or target distracted in melee | `+1` |
| Dim light, smoke, rain, unstable footing | `-1` to `-2` |
| Attacker Blinded | Snag plus `-2` if the target is moving |
| Attacker Reeling | `-2` |
| Attacker Exhausted 2+ | `-1` to `-3` by severity |
| Long range | `-2` |
| Point blank ranged attack while threatened | `-2` unless trained |

## Avoidance

Avoidance is the defender's ability to make a hit fail.

```text
Avoidance = Agility modifier + awareness bonus + stance bonus + cover bonus + condition modifiers - load penalty
```

Agility should carry the most visible weight. A lightly armored rogue can be hard to hit because they move before the blade arrives. A plated Juggernaut can be easy to connect with while still taking less damage.

### Avoidance Modifiers

| Factor | Modifier |
| --- | ---: |
| Light armor or no armor | no load penalty |
| Medium armor | cap Agility contribution at `+2` |
| Heavy armor | cap Agility contribution at `+0` unless a class feature says otherwise |
| Shield raised | `+1` Avoidance against one visible attacker or `+10%` Defense against all attacks |
| Half cover | `+2` Avoidance against ranged attacks |
| Three-quarter cover | `+4` Avoidance against ranged attacks |
| Dodge action | Edge on Avoidance; attacker rolls with Snag |
| Mobile stance | `+2` Avoidance, `-1` Accuracy |
| Guard stance | `+1` Avoidance, `+20%` Defense, `+2` Stability, `-2` Accuracy; moving from the guarded lane ends the stance |
| Prone | melee attackers gain `+2` Accuracy; ranged attackers take `-2` Accuracy |
| Restrained | `-4` Avoidance |
| Stunned, Paralyzed, Unconscious | Avoidance becomes `-5`; many attacks auto-hit if adjacent |
| Invisible | attacker has Snag unless they can reveal the target |

## Defense Percentage

Defense reduces incoming physical damage after the hit lands.

```text
Effective Defense = clamp(base Defense + stance Defense + shield Defense + feature Defense - Armor Break, 0%, cap)
Damage After Defense = floor(modified physical damage * (100% - Effective Defense))
```

Default cap:

| Situation | Defense cap |
| --- | ---: |
| Ordinary combatant | `75%` |
| Unarmored or lightly armored without ward | `45%` |
| Heavy armor specialist | `80%` through class feature |
| Boss with exposed weak points | `60%` to `70%` |
| Siege creature, stone shell, or special armor scene | `85%` by encounter design |

Damage after percentage reduction can reach `0`. That result becomes a Glance if no Ward, temporary HP, or rider converts it into another outcome.

### Recommended Defense Values

| Source | Defense |
| --- | ---: |
| Ordinary clothing | `0%` |
| Heavy coat, padded jack, thick hide | `10%` |
| Light armor | `15%` |
| Reinforced light armor | `20%` |
| Medium armor | `25%` |
| Reinforced medium armor | `30%` |
| Heavy armor | `35%` |
| Reinforced heavy armor | `45%` |
| Passive shield | `+5%` |
| Raised shield | `+10%` against visible attacks, or `+1` Avoidance against one attacker |
| Tower shield or pavise | `+15%`, `-1` Avoidance, setup required |
| Fine armor quality | `+5%` |
| Poor armor quality | `-5%` |
| Guarded status | `+5%` and `+1` Stability |
| Guard stance | `+20%` Defense, `+2` Stability, `+1` Avoidance, `-2` Accuracy; movement from the guarded lane ends the stance |
| Brace action | `+15%` against the next melee or impact hit |
| Spellguard ward shell | usually `+5%` while Ward remains |

### Damage Order

Use this order unless an ability says otherwise.

1. Roll damage dice.
2. Add attack stat, weapon, feature, and condition bonuses.
3. Apply critical dice.
4. Apply vulnerability or resistance.
5. Apply Armor Break to Defense.
6. Apply percentage Defense.
7. Apply Ward or temporary HP.
8. Apply remaining damage to HP.
9. Apply Wound riders if HP damage is above `0`.
10. Apply hit riders that do not require a Wound.

Ward note: personal Ward usually absorbs damage after Defense. Field Ward can absorb before Defense when the ability says it protects the space rather than the body.

### Glancing Hits

A hit becomes a Glance when it lands but deals `0` HP damage after Defense, Ward, Guard, and temporary HP.

Glances can:

- build Juggernaut Momentum
- trigger enemy frustration lines
- preserve a poison coating if no Wound was delivered
- fail to deliver Bleeding, poison, and Wound riders
- still apply some pressure statuses such as Marked or Reeling if the ability says so

Glance messages should show armor doing work.

```text
The knife catches the pauldron and loses its bite. Defense 45% and Ward absorb the hit. Glance.
```

### Minimum Damage Rule

No automatic `1` damage applies to ordinary hits. If the percentage math and protection layers reduce HP damage to `0`, the result is a Glance.

Boss attacks, siege weapons, and special monster traits can declare `minimum 1 Wound` or `minimum 2 Wound` when the fiction supports it.

## Damage Types And Defense

| Damage type | Defense use |
| --- | --- |
| Slashing, piercing, bludgeoning | Full Defense. |
| Bite, claw, horn, slam | Full Defense unless the creature has a bypass trait. |
| Shrapnel, falling debris, thrown stones | Full Defense. |
| Fire, cold, lightning, acid | Use resistance and Resist Checks. Apply Defense only when the effect has a physical carrier. |
| Poison | Delivery may require a Wound; poison effect uses a Resist Check. |
| Psychic, fear, signal, curse | Resist Check lane. |
| Radiant, necrotic, force | Design per ability. Many channels use Resist Checks. |

Physical carrier examples:

| Effect | Defense? |
| --- | --- |
| Stone spike | yes |
| Ice shard | yes |
| Burning oil splash | Defense against impact, Resist Check against Burning |
| Lightning arc through air | no |
| Acid mist | no, unless armor corrosion is the effect |
| Shrapnel burst | yes |
| Fear pulse | no |

## Critical Hits

Critical hits should punch through armor without making Defense meaningless.

Recommended rule:

```text
Critical = natural 20 or margin 10+ when the weapon allows a critical threat
Critical damage = doubled weapon dice
Effective Defense after Armor Break is halved, rounded down
```

Example:

```text
Damage 18
Target Defense 40%
Critical pierce halves Defense to 20%
Final HP damage = floor(18 * 0.80) = 14
```

Weapons can alter this:

| Weapon trait | Critical behavior |
| --- | --- |
| Keen | critical threat on margin `8+` |
| Crushing | on critical, apply Armor Break 1 |
| Piercing | on critical, ignore an extra `10 percentage points` of Defense |
| Heavy | on critical, shove or knockdown check |
| Hooked | on critical, pull or disarm check |

## Armor Break

Armor Break is a short-term percentage-point Defense penalty.

| Break rank | Defense penalty |
| --- | ---: |
| Armor Break 1 | `-10 percentage points` |
| Armor Break 2 | `-20 percentage points` |
| Armor Break 3 | `-30 percentage points` |

Recommended sources:

| Source | Armor Break |
| --- | ---: |
| Pick, mace, hammer strong hit | `1` |
| Acid carrier effect | `1` to `2` |
| Weapon Master crush finisher | `2` |
| Juggernaut shattering release | `1` to all nearby enemies |
| Monster rending bite | `1` |

Armor Break should usually last `1` to `2` rounds. Bosses can have partial resistance so one player cannot strip the whole fight open immediately.

Stacking:

| Rule | Recommendation |
| --- | --- |
| Maximum ordinary Armor Break | `3` |
| Same source repeated | refresh duration, increase rank only if ability says so |
| Different source repeated | stack to cap |
| Boss resistance | reduce incoming break rank by `1` or cap at `1` |

## Shields And Intercepts

Shields can choose between avoidance and reduction.

| Shield use | Effect |
| --- | --- |
| Passive shield | `+5%` Defense. |
| Raised shield | `+10%` Defense against visible attacks or `+1` Avoidance against one visible attacker. |
| Guard ally | Transfer part of an adjacent ally's incoming hit to the shield user before Defense. |
| Shield wall | Requires two trained allies; both gain `+5%` Defense and `+1` Stability. |
| Tower shield set | `+15%` Defense, `-1` Avoidance, cannot use Mobile stance. |

Interception should happen before Defense is applied to HP damage. The intercepting warrior uses their own Defense percentage against the transferred portion.

Example:

```text
An ally would take 12 slashing.
Juggernaut intercepts 8 of it.
Ally resolves 4 damage through their Defense.
Juggernaut resolves 8 damage through Defense 45%.
Juggernaut takes floor(8 * 0.55) = 4 HP damage.
```

## Spells And Resist Checks

Save-based spells stay in their current structure.

```text
Resist Roll = d20 + save bonus + condition bonuses
Spell DC = 8 + training bonus + casting stat modifier + focus bonuses
```

On a failed Resist Check, the target takes the full effect. On a success, the target takes the listed reduced effect. This keeps current spells stable while the weapon side moves to Accuracy, Avoidance, and percentage Defense.

Spell design can use these categories:

| Spell category | Resolution |
| --- | --- |
| Mental pressure, fear, charm, command | Resist Check. |
| Fire burst, frost lock, lightning arc | Resist Check. |
| Poison cloud, disease, corruption | Resist Check. |
| Summoned blade, stone spike, ice shard | Accuracy vs Avoidance, then Defense if physical. |
| Pure force pulse | Ability-specific; usually Resist Check or partial Defense. |
| Healing and shielding | No attack roll; may require line of effect. |

## Saves That Stay Valuable

The new hit system gives Agility a larger role, so saving throws need clear lanes.

| Save | Use |
| --- | --- |
| STR / Might | grapples, shoves, forced movement, heavy restraint |
| DEX / Agility | blasts, traps, falling debris, some area attacks |
| CON / Endurance | poison, disease, bleeding control, exhaustion |
| INT / Reason | illusions, pattern puzzles, memory attacks |
| WIS / Instinct | fear, charm, signal pressure, ambush sense |
| CHA / Presence | possession, domination, oath pressure, social combat |

Spells, hazards, and monster abilities can still target these saves. Defense handles physical punishment. Saves handle the body and mind under pressure.

## Stances

Stances are small, readable combat modes. Most characters can use a basic stance. Classes unlock stronger versions.

| Stance | Effect | Best users |
| --- | --- | --- |
| Neutral | no modifier | default |
| Aggressive | `+2` Accuracy, `-1` Avoidance, `-5%` Defense until next turn | Berserker, duelists |
| Guard | `+1` Avoidance, `+20%` Defense, `+2` Stability, `-2` Accuracy; moving lanes ends the stance | Juggernaut, shield users |
| Mobile | `+2` Avoidance, `-1` Accuracy, cannot use heavy two-handers cleanly | Rogue, Weapon Master |
| Brace | `+3` Stability, `+15%` Defense against the next melee or impact hit | frontliners |
| Aim | `+2` ranged Accuracy, `-2` Avoidance until next turn | archers, crossbow users |
| Press | `+1` Accuracy against the same target each round, resets when changing targets | duelists, bosses |

Stances should appear in the combat menu only when they matter. The text UI can show them as compact choices:

Guard creates a held lane. A guarded character can attack from that lane, intercept through it, and hold a doorway, bridge, breach, or shield wall. Moving to a different lane, taking Mobile, Aim, Aggressive, or Redline ends Guard before the new stance begins.

```text
Stance: Neutral / Guard / Mobile / Aggressive
```

## Conditions In The New Model

| Condition | New combat effect |
| --- | --- |
| Blinded | attacker has Snag; incoming attacks gain `+2` Accuracy if the attacker can see. |
| Burning | end turn fire damage; Defense applies only if the source is physical fuel. |
| Bleeding | end turn damage after a Wound. Endurance Resist Check can stop it. |
| Guarded | `+5%` Defense and `+1` Stability. |
| Marked | attackers gain `+1` Accuracy or class-specific focus-fire benefits. |
| Reeling | `-2` Accuracy. |
| Prone | melee easier to land; ranged harder to land. |
| Restrained | `-4` Avoidance and Snag on Agility Resist Checks. |
| Stunned | cannot act; Avoidance collapses. |
| Invisible | attackers have Snag unless the target is revealed. |
| Armor Broken | Defense reduced by listed percentage-point value. |
| Fixated | affected enemy prefers the source when choosing a target. |
| Braced | increased Stability and Defense against the next impact. |
| Warded | has a Ward pool or field protection layer. |

## Enemy Design

Enemy stat blocks should show both Avoidance and Defense.

```text
Ashen Brand Shieldhand
Accuracy +4
Avoidance +0
Defense 35%
Stability +3
Damage 1d8+2 bludgeoning
Trait: Shield Press, applies Reeling on a strong hit.
```

Fast enemies can have high Avoidance and low Defense. Large enemies can have low Avoidance and high Defense. Elite duelists can have both, with lower HP or sharper weakness tags to keep fights fair.

### Enemy Defense Bands

| Enemy profile | Avoidance | Defense | Notes |
| --- | ---: | ---: | --- |
| Unarmored raider | `+1` to `+3` | `0%` to `10%` | mobile, fragile |
| Leather scout | `+3` to `+5` | `10%` to `15%` | hard to tag, wounds hurt |
| Shieldhand | `+0` to `+2` | `25%` to `40%` | stable line enemy |
| Brute | `-1` to `+1` | `20%` to `35%` | HP carries much of the durability |
| Plated elite | `+0` to `+2` | `40%` to `55%` | needs Armor Break or saves |
| Huge beast | `-2` to `+0` | `20%` to `45%` | easy to hit, hard to drop |
| Warded caster | `+1` to `+3` | `0%` to `15%`, plus Ward | fragile after shell breaks |
| Stone shell creature | `-2` to `+0` | `55%` to `70%` | breakable or weak to saves |

## Player Feedback

Text combat needs to say why damage changed.

Recommended hit messages:

```text
Hit: Mara's axe bites through the guard. 12 damage, Defense 25% -> 9 HP damage.
Glance: The brigand's knife rings off Rhogar's breastplate. Defense 45% and Ward absorb the hit.
Miss: Kaelis turns sideways and the spearhead tears cloak instead of skin.
Critical: The hammer catches the buckle seam. Defense 40% halved to 20%. 14 HP damage.
Resisted: Elira keeps her feet as the flame wash breaks around the cistern stones.
Armor Break: The pick buckles the plate rim. Defense drops by 10 percentage points for 2 rounds.
```

## Migration Notes

The current `armor_class` field can be split into public-facing Avoidance and Defense percentage.

| Current source | New value |
| --- | --- |
| DEX modifier in AC | Avoidance |
| Armor base value | Defense percentage |
| Shield bonus | `+5%` Defense by default, Avoidance when raised |
| Magic armor bonus | `+5%` Defense unless the item says it improves mobility |
| Guarded status | `+5%` Defense and Stability |
| Prone / Restrained AC penalties | Avoidance penalties |

Suggested starter conversion:

| Old armor feel | Avoidance | Defense |
| --- | ---: | ---: |
| Unarmored caster | Agility modifier | `0%` |
| Warded caster | Agility modifier | `0%` to `10%`, plus Ward |
| Light armor rogue | Agility modifier plus light bonuses | `10%` to `15%` |
| Medium armor ranger | Agility modifier capped at `+2` | `25%` |
| Heavy armor fighter | Agility modifier capped at `+0` | `35%` |
| Reinforced heavy tank | Agility modifier capped at `+0` | `45%` |
| Shield user | base Avoidance | Defense `+5%` |

### Draft Shorthand Conversion

Some class drafts use old shorthand such as `+1 Defense`. Convert those values as percentage points.

| Old shorthand | New value |
| --- | ---: |
| `+1 Defense` | `+5% Defense` |
| `+2 Defense` | `+10% Defense` |
| `+3 Defense` | `+15% Defense` |
| `-1 Defense` | `-5% Defense` |
| `ignore 1 Defense` | ignore `10 percentage points` of Defense |
| `Armor Break 1` | `-10 percentage points` |

## First Implementation Slice

1. Add `defense_percent` and `avoidance_bonus` or equivalent derived helpers to combatants.
2. Convert weapon attack resolution from `attack vs AC` to `Accuracy vs Avoidance`.
3. Apply Defense as percentage reduction after physical damage.
4. Keep save-based spells on the current DC/save code path.
5. Add Glance output and block Wound-only riders when no HP damage lands.
6. Convert Guarded, Prone, Restrained, Reeling, and Marked to the new values.
7. Rebalance common enemies with visible fast, armored, and heavy profiles.
8. Tune warrior archetypes around Defense percentage, glances, Armor Break, and Accuracy.

## Balance Targets

| Attacker vs defender | Expected feel |
| --- | --- |
| trained warrior vs ordinary bandit | frequent hits, armor trims damage |
| bandit knife vs plated tank | hits land, low rolls become Glances with Guard or Ward |
| elite duelist vs lightly armored caster | hits often, low Defense makes wounds serious |
| archer vs mobile rogue in cover | many misses unless Marked or revealed |
| spellcaster vs heavy armor | save choice matters more than plate thickness |
| hammer user vs high Defense target | fewer big hits, better Armor Break |

## Open Tuning Questions

- Should Defense use `floor` as drafted, or should very high difficulty use `ceil` to make chip damage more common?
- Should heavy armor reduce initiative, Avoidance, or both?
- Should shields default to `+5%` Defense in code and offer raised-shield Avoidance through a stance?
- Should critical hits halve Defense or subtract a fixed `20 percentage points`?
- Should Armor Break stack to a cap of `3`, or should each source keep separate duration?
- Should spell attacks migrate to Accuracy later, or should all offensive channels use Resist Checks?
