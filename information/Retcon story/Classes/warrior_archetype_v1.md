# Warrior Archetype V1

## Class Role

Warriors solve combat with bodies, reach, leverage, and nerve. They win space first, then turn that space into wounds, protection, or pressure. The new Defense system gives them a clean mechanical home: they care about glancing hits, Armor Break, stances, intercepts, and the exact reason a blade failed to matter.

A warrior's turn should feel like choosing where the fight is allowed to happen. The shield pins a doorway. The hook pulls a raider off the healer. The hammer finds the hinge in borrowed armor. The Bloodreaver leaves a red handprint on an enemy and everyone near it starts breathing easier.

Defense values in this draft use percentages. Old shorthand such as `+1 Defense` should be read as `+5% Defense`, and `Armor Break 1` means `-10 percentage points`.

## Shared Warrior Rules

### Primary Stats

| Stat | Warrior use |
| --- | --- |
| Might / STR | Heavy weapon Accuracy, shove pressure, Armor Break, carry weight, Stability. |
| Agility / DEX | Avoidance, initiative, light weapon Accuracy, mobile stances. |
| Endurance / CON | HP, Wound recovery, Bleeding control, fatigue resistance. |
| Presence / CHA | taunts, commands, morale pressure, some Bloodreaver healing calls. |
| Instinct / WIS | threat reads, intercept timing, ambush response. |

Warrior builds can lean hard into Might and Endurance, but Agility stays relevant because hit chance now lives outside Defense.

### Baseline Durability

Recommended starting profile:

| Value | Recommendation |
| --- | --- |
| Hit die feel | highest or near-highest HP tier |
| Armor access | all armor categories |
| Shield access | all shields |
| Weapon access | all mundane weapons plus martial techniques |
| Base Defense scaling | from armor, shield, stance, and archetype passives |
| Base Avoidance scaling | from Agility, load, stance, and selected techniques |
| Save strengths | Might / STR and Endurance / CON |

### Warrior Resource: Grit

Grit is the shared martial resource. It represents breath control, pain tolerance, timing, and the ugly calm that arrives after the first blow lands.

Recommended rules:

```text
Maximum Grit = 2 + training bonus + Endurance modifier, minimum 2
Start combat with 1 Grit
Gain 1 Grit when you take a Wound, score a strong hit, intercept for an ally, or turn a hit into a Glance
Spend Grit on archetype techniques, stance spikes, and emergency protection
Lose all temporary Grit when combat ends
```

Grit should move often enough to feel alive. It should avoid becoming a second mana bar.

### Shared Warrior Actions

| Action | Cost | Effect |
| --- | --- | --- |
| Strike | action | Weapon attack using Accuracy vs Avoidance. |
| Guard | action or stance by feature | Gain strong Defense percentage, Stability, and lane control until next turn. |
| Intercept | reaction or bonus action by feature | Take part of an adjacent ally's incoming hit before Defense percentage applies. |
| Shove | action | Might vs Stability; push, knock prone, or break formation. |
| Pin | action | Weapon attack; on strong hit, applies Reeling or Fixated. |
| Rally | bonus action, 1 Grit | Clear Reeling from self or grant Guarded 1 to an ally. |
| Weapon Read | bonus action | Identify whether the target has high Defense, high Avoidance, Armor Break weakness, or resistance. |
| Brace | stance | Gain Stability and Defense percentage against the next impact. |

### Weapon Families

Warriors should care about weapon shape. A spear, axe, mace, and greatsword can share the same basic attack system while creating different tactical questions.

| Family | Main job | Combat hook |
| --- | --- | --- |
| Blades | reliable Wounds | stronger crits, Bleeding access, good against low Defense |
| Axes | burst and cleave | damage spills on strong hits, good against clustered enemies |
| Maces and hammers | armor pressure | Armor Break and Stability damage |
| Spears and polearms | reach control | intercept, pin, first-strike pressure |
| Shields | protection and tempo | Defense, Guard, shove, ally cover |
| Paired weapons | hit fishing | higher chance to trigger marks, lower single-hit damage |
| Heavy two-handers | high damage | lower Avoidance, better critical and break effects |
| Throwing weapons | flexible targeting | mark support, low commitment ranged pressure |

### Shared Warrior Stances

| Stance | Effect | Notes |
| --- | --- | --- |
| Guard | `+20%` Defense, `+2` Stability, `+1` Avoidance, `-2` Accuracy; leaving the guarded lane ends the stance | baseline frontline stance |
| Press | `+1` Accuracy against the same target each round | dueling and boss pressure |
| Brace | `+15%` Defense against next physical hit, `+3` Stability | chokepoint stance |
| Aggressive | `+2` Accuracy, `-5%` Defense, `-1` Avoidance | burst stance |
| Mobile | `+2` Avoidance, `-1` Accuracy | light armor and Weapon Master stance |

Guard is a lane pledge. The warrior plants their boots, sets the shield or weapon angle, and dares the enemy to spend force on the place they picked. Guard can stack with a passive shield, but Mobile, Aim, Aggressive, and Redline replace it.

### Shared Passive Tags

| Passive | Effect |
| --- | --- |
| Armor Habit | Reduce heavy armor load penalty by `1`. |
| Hard Lesson | Gain `1` Grit the first time each combat you take a Wound. |
| Line Fighter | Adjacent allies gain `+1` Stability while you are conscious. |
| Close Measure | Gain `+1` Accuracy against enemies you attacked last round. |
| Scar Tissue | `+1` Endurance Resist Checks against Bleeding, poison delivery, and fatigue. |
| Weapon Familiarity | Choose one weapon family; gain `+1` Accuracy or `+1` damage with it. |
| Shield Hand | Shields can be raised as a bonus action. |
| Veteran's Eye | Weapon Read also reveals the target's lowest physical defense lane. |

## Level Progression

This follows the broader choice-based progression draft while giving Warrior its own texture.

| Level | Warrior progression |
| ---: | --- |
| 1 | Choose Warrior. Gain Strike, Guard, Shove, one weapon family training, and one Tier 1 technique. |
| 2 | Choose one Tier 1 technique or passive. Gain Grit. |
| 3 | Choose Juggernaut, Bloodreaver, Berserker, or Weapon Master. Gain signature feature and one subclass technique. |
| 4 | Choose class or subclass technique. Choose stat increase or feat. |
| 5 | Power spike: gain Extra Strike or an archetype equivalent. Upgrade one known technique. |
| 6 | Choose utility technique and passive. Unlock improved stances. |
| 7 | Choose subclass specialization path. |
| 8 | Choose any known-tier technique. Choose stat increase or feat. |
| 9 | Gain advanced technique. Master one existing technique. |
| 10 | Choose capstone. Gain final archetype passive. |

### Extra Strike

At level 5, most Warriors gain Extra Strike: once per turn after taking the Strike action, make a second weapon attack with `-2` Accuracy. Archetypes can replace or alter this:

| Archetype | Level 5 spike |
| --- | --- |
| Juggernaut | Extra Strike or Heavy Reprisal after a Glance. |
| Bloodreaver | Extra Strike or Bloodletting Pulse after a marked Wound. |
| Berserker | Extra Strike with self-Defense penalty. |
| Weapon Master | Extra Strike with combo generation and style switching. |

## Archetype 1: Juggernaut

### Combat Read

Juggernauts are armored anchors. They invite contact, flatten momentum, and make enemies spend actions on the worst possible target. Defense reduction and Glance rules are their playground.

The Juggernaut's fantasy is simple at the table: the enemy hits them, the hit loses its teeth, and the warrior turns that insult into forward motion.

### Role

| Role axis | Juggernaut position |
| --- | --- |
| Party role | Tank |
| Damage style | steady impact, retaliatory bursts |
| Protection style | taunt, intercept, Guard, damage transfer |
| Preferred armor | heavy armor, shield, tower shield, reinforced mail |
| Preferred weapons | shield and mace, polearm, hammer, axe, heavy blade |
| Primary stats | Endurance, Might |
| Secondary stats | Presence, Instinct |
| Weak points | magic saves, forced movement, kiting, Armor Break |

### Resource: Momentum

Momentum is a Juggernaut rider on Grit.

```text
Momentum cap = 6
Gain 1 Momentum when Defense removes 30% or more of a hit's physical damage
Gain 1 Momentum when an incoming hit becomes a Glance
Gain 1 Momentum when you intercept damage for an ally
Gain 1 Momentum when a Fixated enemy attacks you
Spend Momentum on releases, heavy guards, and taunt spikes
Momentum fades by 1 at the end of your turn if you neither took nor dealt physical pressure since your last turn
```

Momentum should reward standing where the fight is hottest.

### Signature Feature: Iron Draw

When the Juggernaut enters Guard or Brace stance, they can mark one enemy within melee reach or shouting distance as Fixated until the start of the Juggernaut's next turn.

Fixated enemies:

- prefer the Juggernaut as a target when their AI can justify it
- take `-1` Accuracy against targets other than the Juggernaut
- grant the Juggernaut `1` Momentum when they hit the Juggernaut

Bosses can resist Fixated through a Presence or Instinct Resist Check, but even a resisted taunt can apply `-1` Accuracy for one attack.

### Juggernaut Techniques

| Technique | Tier | Cost | Effect |
| --- | ---: | --- | --- |
| Shoulder In | 1 | 1 Grit | Move into Guard and gain `+5%` Defense until next turn. If already Guarding, gain `1` Momentum. |
| Lock The Door | 1 | action | Choose a lane or adjacent ally. Enemies crossing it trigger a shove or pin attempt. |
| Hard Stop | 1 | reaction, 1 Grit | Transfer part of an adjacent ally's incoming physical damage to yourself, then resolve it through your Defense. |
| Iron Draw | signature | bonus action | Apply Fixated to one enemy. Stronger in Guard stance. |
| Plate Answer | 2 | 2 Momentum | After a Glance, strike the attacker with `+2` Accuracy. |
| Wall Breath | 2 | 1 Grit | Gain temporary HP equal to Endurance modifier + training bonus. If hit this round, also gain Guarded 1. |
| Low Center | 2 | passive | Gain `+2` Stability in heavy armor and resist forced movement with Edge. |
| Hammer The Space | 2 | action, 2 Momentum | AoE shove against adjacent enemies. Deals small bludgeoning damage on failed Stability. |
| Weight Of The Line | 3 | stance upgrade | Guard stance also gives adjacent allies `+5%` Defense. |
| Shattering Reprisal | 3 | 3 Momentum | Counterattack after absorbing damage. On hit, apply Armor Break 1. |
| Doorframe Saint | 3 | passive | Once per combat, when an ally behind you would be dropped, intercept half the damage before Defense percentage is applied. |
| Earth Nail | 3 | action, 2 Grit | Pin one enemy. On hit, apply Reeling and Fixated. On strong hit, also reduce their movement. |
| Bell-Ring Release | 4 | 4 Momentum | Impact burst against all adjacent enemies. Deals weapon damage, applies Reeling, and Armor Break 1 on strong hit. |
| No Backward Step | 4 | passive | While below half HP, Guard stance grants an extra `+5%` Defense and Fixated lasts one additional attack. |
| Black Gate | capstone | 5 Momentum, 1 Grit | For one round, intercept the first hit against each adjacent ally. Each intercepted hit can become a Glance through your Defense. |

### Juggernaut Specialization Paths

| Path | Focus | Features |
| --- | --- | --- |
| Bastion | ally protection | stronger intercepts, shield wall, shared Defense |
| Breaker | counter-damage | Armor Break, knockdown, impact bursts |
| Iron Saint | survival | temp HP, condition resistance, bleed control |

### Juggernaut Upgrade Examples

| Base technique | Upgrade | Effect |
| --- | --- | --- |
| Hard Stop | Clean Catch | If Defense and protection layers reduce the intercepted hit to `0`, restore `1` Grit. |
| Iron Draw | Voice Like A Gate | Fixated can affect two enemies with lower duration. |
| Plate Answer | Hinge Strike | Counterattack gains Armor Break on a strong hit. |
| Wall Breath | Slow Heart | Also improves Endurance Resist Checks until next turn. |
| Bell-Ring Release | Tollhouse Fall | Enemies that fail Stability are knocked Prone. |

### Juggernaut Combat Loop

1. Enter Guard or Brace.
2. Fixate a dangerous enemy.
3. Turn hits into reduced damage or Glances.
4. Build Momentum.
5. Spend Momentum on counterattacks, Armor Break, or AoE control.
6. Intercept when an ally would take a bad hit.

### Juggernaut Tuning Notes

- Their damage should feel dependable, with bursts after pressure builds.
- They should become weaker when enemies ignore them, fly away, force saves, or strip Defense.
- They should be excellent in narrow rooms and messy when the fight spreads across open ground.
- Glance text is part of their reward loop. The player should see armor doing work.

## Archetype 2: Bloodreaver

### Combat Read

Bloodreavers are violent sustain supports. They heal by making wounds useful. Their best turns mark an enemy, cut it open, and let nearby allies recover through the rhythm of damage dealt.

They work well in Aethrune because the frontier already keeps ledgers on everything. A Bloodreaver treats pain like an account that can be moved, but the ink is warm and everyone can smell the iron.

### Role

| Role axis | Bloodreaver position |
| --- | --- |
| Party role | Heal |
| Damage style | sustained melee, marks, Bleeding |
| Healing style | damage-linked healing, delayed recovery, emergency transfer |
| Preferred armor | medium armor, heavy armor if built for Endurance |
| Preferred weapons | axes, blades, hooked weapons, paired weapons |
| Primary stats | Endurance, Might |
| Secondary stats | Presence, Agility |
| Weak points | enemies without blood, high Defense targets, being unable to attack |

### Resource: Blood Debt

Blood Debt tracks pain the Bloodreaver can redirect.

```text
Blood Debt cap = 5
Gain 1 Blood Debt when you deal a Wound to a marked or Bleeding enemy
Gain 1 Blood Debt when you take a Wound
Gain 1 Blood Debt when an adjacent ally takes a Wound and you are conscious
Spend Blood Debt to heal, transfer harm, empower marks, or detonate Bleeding
Blood Debt clears after combat
```

Healing should be tied to contact, risk, and target selection.

### Signature Feature: Red Mark

Mark one enemy for `3` rounds. The first ally each round who deals a Wound to that enemy heals for `1 + Bloodreaver training bonus`. The Bloodreaver gains `1` Blood Debt when Red Mark healing triggers.

If the marked enemy dies, the Bloodreaver can move the mark as a bonus action on their next turn.

### Bloodreaver Techniques

| Technique | Tier | Cost | Effect |
| --- | ---: | --- | --- |
| Red Mark | signature | bonus action | Mark enemy. Wounds against it heal the attacker or weakest nearby ally. |
| Blood Price | 1 | 1 Blood Debt | Heal an adjacent ally for `1d4 + Endurance modifier`; Bloodreaver takes Reeling 1. |
| War-Salve Strike | 1 | action | Weapon attack. On Wound, heal the lowest-HP ally for half training bonus, minimum 1. |
| Draw Pain | 1 | reaction, 1 Blood Debt | Reduce an ally's incoming damage by `2 + Endurance modifier`; take half that prevented amount as true damage. |
| Butcher's Mercy | 1 | passive | Healing from Red Mark increases by `1` when the Bloodreaver is below half HP. |
| Open The Ledger | 2 | action, 1 Grit | Attack a Red Mark target with `+1` Accuracy. On Wound, apply Bleeding. |
| Red Thread | 2 | 2 Blood Debt | Connect two allies until next turn. When one is healed by Bloodreaver technique, the other heals for half. |
| Clot Command | 2 | bonus action | Attempt Endurance or Presence check to stop Bleeding on an ally. Success also heals `1`. |
| Feast The Line | 2 | 2 Blood Debt | For one round, all allies gain `+1` damage against the Red Mark target and heal `1` on Wound. |
| Borrowed Pulse | 3 | reaction, 3 Blood Debt | When an ally drops to `0`, they remain at `1` HP until end of round. If the marked enemy is Wounded before then, the ally stabilizes at `1`. |
| Red Harvest | 3 | action, 2 Grit | Cleave attack. Each Wounded enemy grants `1` healing split among allies. |
| Bitter Surgeon | 3 | passive | Healing techniques also clear Reeling or reduce Bleeding duration by `1`. |
| Blood Bell | 4 | 4 Blood Debt | Detonate Bleeding on enemies in reach. Allies heal for a portion of total damage dealt. |
| Debt Collector | 4 | passive | When a Red Mark target dies, restore `1` Grit and move `1` Blood Debt into healing for the weakest ally. |
| The Red Ledger Closes | capstone | 5 Blood Debt | For one round, every Wound the party deals to the Red Mark target heals the most injured ally. If the target dies, all allies gain Guarded 1. |

### Bloodreaver Specialization Paths

| Path | Focus | Features |
| --- | --- | --- |
| Field Butcher | damage-linked healing | stronger Red Mark, Bleeding detonation |
| Pain-Binder | protection | Draw Pain upgrades, emergency saves |
| Red Captain | party aggression | ally damage buffs, shared healing windows |

### Bloodreaver Upgrade Examples

| Base technique | Upgrade | Effect |
| --- | --- | --- |
| Red Mark | Fresh Ink | First Wound each round also applies Reeling 1. |
| Draw Pain | Take Mine Instead | Prevented damage passes through Bloodreaver Defense before self-damage. |
| War-Salve Strike | Clean Cut | On strong hit, healing can target two allies. |
| Red Thread | Knot The Vein | Linked allies also share Guarded 1. |
| Blood Bell | Toll Paid | If Blood Bell drops an enemy, restore `1` Blood Debt. |

### Bloodreaver Combat Loop

1. Mark the target the party can reliably Wound.
2. Attack to build Blood Debt.
3. Spend Blood Debt to patch allies or redirect danger.
4. Keep Bleeding active when the fight will last.
5. Detonate or close the mark when the enemy is near death.

### Bloodreaver Tuning Notes

- Healing should fall sharply when the Bloodreaver cannot reach enemies.
- Constructs, spirits, and sealed armor enemies should force alternate play.
- Red Mark should reward party focus fire without making every fight a single-target race.
- Self-damage must be readable. The player should know when a rescue costs the Bloodreaver's own blood.

## Archetype 3: Berserker

### Combat Read

Berserkers trade safety for pressure. They lower their own Defense, draw wounds, and turn low HP into damage. They should feel like a door kicked off its hinges: direct, loud, and dangerous to stand near.

The class needs restraint in tuning. A Berserker should flirt with collapse and still give the player tools to pull back.

### Role

| Role axis | Berserker position |
| --- | --- |
| Party role | DPS |
| Damage style | sustained aggression, burst windows, execute pressure |
| Protection style | self-healing on Wound, temporary HP, kill momentum |
| Preferred armor | light or medium armor; heavy armor for slower bruiser builds |
| Preferred weapons | axes, greatswords, paired blades, mauls |
| Primary stats | Might, Endurance |
| Secondary stats | Agility, Presence |
| Weak points | control effects, ranged kiting, heal denial, burst magic |

### Resource: Fury

Fury rises as the Berserker takes risks.

```text
Fury cap = 6
Gain 1 Fury when you take a Wound
Gain 1 Fury when you hit in Aggressive stance
Gain 1 Fury when you drop below half HP for the first time each combat
Gain 1 Fury when you reduce an enemy to 0 HP
Spend Fury on burst attacks, temporary HP, and self-healing
Fury falls by 1 when you end a turn without attacking or being attacked
```

### Bloodied Bands

Berserker features can read HP bands.

| HP band | Name | Effect direction |
| --- | --- | --- |
| 70% or higher | cold blood | stable, lower bonuses |
| 30% to 69% | red work | main damage bonuses |
| 29% or lower | last room | high damage, higher risk |

Avoid a design where the best Berserker is always almost dead. The strongest features should include escape valves, temp HP, or one-round limits.

### Signature Feature: Redline

As a bonus action, enter Redline until the start of your next turn.

Effects:

- gain `+2` Accuracy
- gain `+1` damage per Fury spent, up to `3`
- lose `5%` Defense and `1` Avoidance during the window
- if the attack deals a Wound, regain HP equal to training bonus

Redline makes the Berserker's bargain visible.

### Berserker Techniques

| Technique | Tier | Cost | Effect |
| --- | ---: | --- | --- |
| Redline | signature | bonus action, up to 3 Fury | Accuracy and damage burst, temporary Defense loss. |
| Reckless Cut | 1 | action | Strike with `+2` Accuracy. Incoming attacks gain `+1` Accuracy against you until next turn. |
| Teeth Set | 1 | 1 Fury | Gain temp HP equal to training bonus + Endurance modifier. |
| Break Mood | 1 | passive | First Wound you take each combat grants Fury and clears Reeling. |
| Rattle Them | 1 | bonus action | Presence pressure against nearby enemy. On success, apply Reeling 1. |
| Split Guard | 2 | action, 1 Fury | Heavy attack. On strong hit, apply Armor Break 1. |
| Drink The Hurt | 2 | 2 Fury | After Wounding an enemy, heal for `1d4 + Endurance modifier`. |
| Hook And Ruin | 2 | action | Attack and pull target closer on strong hit. If target is Bloodied, gain `1` Fury. |
| All Teeth | 2 | stance upgrade | Aggressive stance grants one extra damage die on critical hits. |
| Red Work Rhythm | 3 | passive | While between 30% and 69% HP, gain `+1` damage and `+1` Stability. |
| Last Room Laugh | 3 | reaction, 3 Fury | When damage would drop you to `0`, stay at `1` HP until end of next turn. Heal if you Wound an enemy before then. |
| Ruin Swing | 3 | action, 2 Fury | Wide attack against two adjacent enemies. Each Wound restores `1` Fury, once per target. |
| No Door Left | 4 | 4 Fury | Charge to an enemy, attack with `+2` Accuracy, and shove on hit. Lose Guarded if present. |
| Black-Mouth Focus | 4 | passive | At 29% HP or lower, Redline heals for double training bonus once per round. |
| End It Here | capstone | 5 Fury | Single-target strike. Damage increases as HP falls. If it drops the target, gain temp HP and clear one harmful condition. |

### Berserker Specialization Paths

| Path | Focus | Features |
| --- | --- | --- |
| Red Cleaver | multi-target pressure | cleaves, charge lines, kill chaining |
| Scar-Heart | survival | temp HP, self-heal, last-chance windows |
| War Howl | morale pressure | Reeling, fear pressure, ally aggression |

### Berserker Upgrade Examples

| Base technique | Upgrade | Effect |
| --- | --- | --- |
| Reckless Cut | Meaner Than Sense | If the hit becomes a critical, regain `1` Fury. |
| Teeth Set | Blood Under Nails | Temp HP also grants `+1` Stability. |
| Drink The Hurt | Bitter Mouthful | Healing increases against Red Mark, Bleeding, or Armor Broken targets. |
| Last Room Laugh | Still Standing | If the save window succeeds, clear Prone or Restrained. |
| End It Here | Name On The Floor | On kill, nearby enemies make Presence Resist Check or become Reeling. |

### Berserker Combat Loop

1. Choose a target that can be Wounded quickly.
2. Enter Aggressive or Redline.
3. Build Fury through hits, wounds taken, and kills.
4. Spend Fury before control effects shut the turn down.
5. Use Teeth Set, Drink The Hurt, or Last Room Laugh to avoid collapse.

### Berserker Tuning Notes

- Berserker damage should beat other warrior paths during risky windows.
- Their Defense penalties should matter in the new damage reduction model.
- Low-HP bonuses should tempt the player, then ask for a decision.
- Their self-healing should require Wounds, so high Defense enemies create friction.

## Archetype 4: Weapon Master

### Combat Read

Weapon Masters are technical fighters. They switch forms, read enemy defenses, and build combos by changing how they attack. They should feel sharp in the player's hands: less raw damage than Berserker at first glance, more answers across a long fight.

They are the warrior who notices a buckle, a limp, a loose shield strap, and the way a frightened guard keeps protecting the wrong rib.

### Role

| Role axis | Weapon Master position |
| --- | --- |
| Party role | DPS |
| Damage style | adaptive single-target and controlled cleave |
| Protection style | parry, footwork, disarm, stance choice |
| Preferred armor | light or medium armor |
| Preferred weapons | multiple weapon families, paired sets, versatile weapons |
| Primary stats | Might or Agility by build |
| Secondary stats | Instinct, Endurance |
| Weak points | resource disruption, simple swarm pressure, enemies with few readable weaknesses |

### Resource: Combo

Combo rewards varied technique.

```text
Combo cap = 5
Gain 1 Combo when you hit with a weapon family or stance you did not use last turn
Gain 1 Combo when Weapon Read reveals a weakness
Gain 1 Combo when you exploit Armor Broken, Prone, Marked, or Reeling
Spend Combo on finishers, reaction parries, and style swaps
Combo resets to 0 after two turns without landing a weapon hit
```

### Signature Feature: Style Wheel

Choose three trained styles. The default set is Cleave, Pierce, and Crush.

| Style | Best target | Effect |
| --- | --- | --- |
| Cleave | groups, low Defense | strong hit spills damage to nearby enemy |
| Pierce | high Avoidance, low Defense | `+1` Accuracy; critical ignores extra Defense |
| Crush | high Defense, shield users | strong hit applies Armor Break 1 |
| Hook | mobile enemies | pull, disarm, or apply Reeling |
| Guarded Point | duelists | parry reaction and riposte |
| Throw | distant or exposed enemies | mark setup and flexible targeting |

The Weapon Master can switch style once per turn for free. Additional swaps cost Combo or a bonus action.

### Weapon Master Techniques

| Technique | Tier | Cost | Effect |
| --- | ---: | --- | --- |
| Style Wheel | signature | free once per turn | Switch trained style. Gain Combo when style choice exploits target profile. |
| Measure Twice | 1 | bonus action | Weapon Read. If it reveals a weakness, gain `1` Combo. |
| Clean Line | 1 | action | Pierce attack with `+1` Accuracy. On strong hit, next attack against target gains `+1` Accuracy. |
| Broad Cut | 1 | action | Cleave attack. On strong hit, splash small damage to adjacent enemy. |
| Dent The Shell | 1 | action | Crush attack. On Wound or strong hit, apply Armor Break 1. |
| Handful Of Distance | 1 | reaction, 1 Combo | Gain `+2` Avoidance against one melee attack. |
| Switch Grip | 2 | free, 1 Combo | Swap style after seeing hit result but before damage. |
| First Flaw | 2 | passive | First successful Weapon Read each combat grants `+1` Accuracy against that target. |
| Hook The Guard | 2 | action | On hit, remove Guarded or lower target Stability. |
| Second Answer | 2 | 2 Combo | After hitting with one style, make a follow-up with a different style at `-2` Accuracy. |
| Table Of Cuts | 3 | passive | Maintain Combo when changing targets if the new target shares the same weakness. |
| Quiet Finish | 3 | 3 Combo | Single-target finisher. Damage increases if target is Armor Broken, Prone, or Reeling. |
| Break Pattern | 3 | reaction, 2 Combo | When an enemy repeats the same attack, gain Guarded 1 and make a counterattack if it misses. |
| Three Lessons | 4 | 4 Combo | Make three attacks, each with a different style. Each attack after the first uses `-2` Accuracy. |
| No Bad Weapon | 4 | passive | Improvised and secondary weapons use your best trained weapon family bonus. |
| The Final Measure | capstone | 5 Combo | Read the target, choose its weakest physical lane, then strike. On hit, ignore part of Defense and apply a style rider. |

### Weapon Master Specialization Paths

| Path | Focus | Features |
| --- | --- | --- |
| Duelist | single-target precision | parry, riposte, critical pressure |
| Arsenal | many weapon families | faster swaps, improvised weapons, broad matchup control |
| Breaker-Savant | weakness exploitation | Armor Break, stance disruption, boss reads |

### Weapon Master Upgrade Examples

| Base technique | Upgrade | Effect |
| --- | --- | --- |
| Measure Twice | Look Once | Weapon Read becomes free after initiative if you are alert. |
| Clean Line | Needle Gap | Pierce hit ignores `10 percentage points` of Defense against Armor Broken targets. |
| Dent The Shell | Bell Crack | Armor Break lasts one extra round on strong hit. |
| Switch Grip | Turn The Wrist | Also converts one damage type among slashing, piercing, or bludgeoning. |
| Three Lessons | Old Yard Drill | If all three attacks hit, restore `1` Combo. |

### Weapon Master Combat Loop

1. Read the target.
2. Pick a style that attacks the target's weaker lane.
3. Build Combo by varying style and exploiting conditions.
4. Use reactions to survive through footwork instead of raw Defense.
5. Spend Combo on finishers or multi-style bursts.

### Weapon Master Tuning Notes

- Weapon Master should reward attention to enemy tags.
- Their UI needs concise weakness labels: `High Defense`, `Low Avoidance`, `Breakable`, `Bleeds`, `Heavy Guard`.
- They should feel stronger in long fights than quick ambushes.
- Their best damage needs setup; their baseline attack should remain reliable.

## Warrior Ability Tiers

### Tier 1: Levels 1-3

Tier 1 abilities establish the play pattern.

| Ability | Archetype | Use |
| --- | --- | --- |
| Shoulder In | Juggernaut | enter Guard and build pressure |
| Blood Price | Bloodreaver | emergency small heal |
| Reckless Cut | Berserker | early risk attack |
| Measure Twice | Weapon Master | read enemy defenses |
| Rally | shared | light support |
| Weapon Familiarity | shared | build definition |

### Tier 2: Levels 3-6

Tier 2 abilities make the subclass work in a party.

| Ability | Archetype | Use |
| --- | --- | --- |
| Plate Answer | Juggernaut | reward Glances |
| Red Thread | Bloodreaver | linked healing |
| Drink The Hurt | Berserker | sustain during aggression |
| Second Answer | Weapon Master | combo follow-up |

### Tier 3: Levels 5-8

Tier 3 abilities add fight-shaping tools.

| Ability | Archetype | Use |
| --- | --- | --- |
| Doorframe Saint | Juggernaut | save ally from collapse |
| Borrowed Pulse | Bloodreaver | delayed death prevention |
| Last Room Laugh | Berserker | one-turn survival promise |
| Quiet Finish | Weapon Master | exploit condition setup |

### Tier 4: Levels 9-10

Tier 4 abilities define the endgame style.

| Ability | Archetype | Use |
| --- | --- | --- |
| Black Gate | Juggernaut | party-wide intercept round |
| The Red Ledger Closes | Bloodreaver | focus-fire healing climax |
| End It Here | Berserker | execute and recover |
| The Final Measure | Weapon Master | read and punish weakest lane |

## Feat Ideas For Warriors

| Feat | Effect |
| --- | --- |
| Shield-Bound | Shield Guard can protect an adjacent ally once per round. |
| Armor Sleeper | Sleep, poison, and fatigue checks gain `+1` while wearing medium or heavy armor. |
| Hook Fighter | Hooked weapons gain pull or disarm rider on strong hit. |
| Close Yard Killer | Gain `+1` Accuracy against targets that missed you last round. |
| Scarred Calm | Once per combat, taking a Wound grants Guarded 1 and clears Frightened. |
| Red Work Apprentice | Non-Bloodreavers can place a weaker Red Mark once per combat. |
| Stance Dancer | Swap stance once per turn without spending bonus action. |
| Breaker Training | Crushing weapons apply Armor Break on margin `8+` instead of `10+`. |

## Equipment Hooks

| Item trait | Warrior interaction |
| --- | --- |
| Reinforced | `+5%` Defense, heavier load. |
| Balanced | `+1` Accuracy when switching stance. |
| Serrated | Bleeding rider requires Wound. |
| Hooked | pull, disarm, or Reeling rider on strong hit. |
| Piercing | critical ignores extra Defense. |
| Crushing | Armor Break on strong hit. |
| Guarded hilt | `+1` to parry reactions. |
| Tower frame | stronger ally cover, lower Avoidance. |
| Old service mark | bonus Presence for taunts or command checks in military scenes. |

## Party Synergies

| Partner style | Warrior synergy |
| --- | --- |
| Rogue / Assassin | Juggernaut Fixated and Weapon Master Reeling create safer burst windows. |
| Rogue / Poisoner | Bloodreaver Bleeding and Poisoner attrition stack pressure if Wounds land. |
| Mage / Elementalist | Juggernaut pins targets inside zones. Weapon Master reads elemental carriers with the right passive. |
| Mage / Aethermancer | Shields stack cleanly with Defense but should avoid making Glances automatic. |
| Rogue / Alchemist | Berserker loves temp HP and emergency condition clearing. |
| Mage / Spellguard | Two-front protection: Spellguard handles channels, Juggernaut handles bodies. |

## Enemy Counters

| Counter | Best against | Why |
| --- | --- | --- |
| Armor Break enemies | Juggernaut | cuts into Defense and Glance loop |
| High Defense enemies | Berserker, Bloodreaver | blocks Wound-linked healing and self-heal |
| High Avoidance duelists | Berserker | punishes low-Accuracy burst swings |
| Flying or distant enemies | Juggernaut, Bloodreaver | deny contact and intercept lanes |
| Save-heavy casters | all Warriors | target Resist Checks instead of Defense |
| Swarms | Weapon Master duelists | split attention and reset combo plans |
| Wound-proof constructs | Bloodreaver | reduce blood economy |

## UI Presentation

Warrior turns should show the current stance and special resource.

```text
Rhogar - HP 31/38 - Defense 40% - Avoidance +0 - Stance: Guard - Grit 3 - Momentum 2
```

Attack summaries should show why the result happened.

```text
The mace hits. 8 bludgeoning, Defense 40% -> 4 HP damage. Momentum +1.
The knife lands and skates off the pauldron. Glance. Momentum +1.
Red Mark pays out: Kaelis heals 3 HP from the Wound.
Weapon Read: shieldhand has high Defense, low Avoidance, weak to Crush.
```

## Implementation Notes

Recommended first warrior slice:

1. Implement Defense, Avoidance, and Glance in weapon attacks.
2. Give the base Warrior Grit, Guard, Shove, and Weapon Read.
3. Implement Juggernaut first because it tests Defense reduction directly.
4. Add Bloodreaver after Wound-only riders are reliable.
5. Add Berserker after self-damage, temporary HP, and low-HP checks are stable.
6. Add Weapon Master after weapon family tags and enemy weakness labels exist.

## Open Design Questions

- Should Warrior replace Fighter, Barbarian, and Paladin in the public class list, or sit above them as an archetype family during migration?
- Should Bloodreaver healing scale from damage dealt, training bonus, Endurance, or a mix?
- Should Juggernaut taunts use Presence Resist Checks or simple AI weighting?
- Should Berserker self-healing trigger on any Wound or only weapon Wounds?
- Should Weapon Master require multiple equipped weapons, or can one versatile weapon support multiple styles?
- Should Grit exist for every Warrior archetype, or should each subclass use only its own resource?
