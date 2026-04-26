# Rogue Archetype V1

## Class Role

Rogues solve combat with position, timing, leverage, tools, and unfair information. The combat redesign gives them a sharp job: Agility and Avoidance make enemies miss, while low Defense keeps every Wound dangerous. Rogues live in the gap between a near miss and a fatal mistake.

A rogue turn should feel quick and specific. Chalk dust on the sill. A false bootstep behind the guard. A vial thumbed open in the sleeve. A blade set exactly where armor ends and panic begins.

Defense values in this draft use percentages. Old shorthand such as `+1 Defense` should be read as `+5% Defense`, and `Armor Break 1` means `-10 percentage points`.

## Shared Rogue Rules

### Primary Stats

| Stat | Rogue use |
| --- | --- |
| Agility / DEX | Avoidance, initiative, finesse Accuracy, stealth, acrobatics |
| Reason / INT | traps, alchemy, poison craft, tactical reads, weak-point setup |
| Instinct / WIS | ambush sense, threat reads, survival, lie detection |
| Presence / CHA | misdirection, feints, social combat, fear pressure |
| Endurance / CON | poison tolerance, field survival, concentration under Wounds |
| Might / STR | grapples, climbing under load, brutal ambush variants |

Rogues should have the highest natural Avoidance curve and one of the lowest Defense curves. They survive by denying clean hits, breaking target priority, and making enemies waste turns.

### Baseline Durability

Recommended starting profile:

| Value | Recommendation |
| --- | --- |
| Hit die feel | medium-low HP tier |
| Armor access | clothing, light armor, flexible medium armor by feature |
| Shield access | none by default |
| Weapon access | knives, short blades, bows, crossbows, thrown weapons, tools |
| Base Defense scaling | low from gear, brief spikes from tricks |
| Base Avoidance scaling | high from Agility, stealth, stance, cover, decoys |
| Save strengths | Agility / DEX and Reason / INT or Instinct / WIS by archetype |

### Rogue Resource: Edge

Edge is the shared Rogue tempo resource. It represents initiative seized through position, confusion, concealment, and dirty timing.

```text
Edge cap = 5
Start combat with 1 Edge if not Surprised
Gain 1 Edge when an enemy misses you by 4 or less
Gain 1 Edge when you enter stealth, exploit cover, apply a trick condition, or hit a target that is Marked, Prone, Reeling, Poisoned, or isolated
Spend Edge on evasions, bonus actions, precision riders, tricks, and archetype releases
Edge fades by 1 at the end of your turn if you are exposed and did not move, hide, attack, or use a trick
```

Edge should make Rogue turns feel reactive without becoming passive.

### Shared Rogue Actions

| Action | Cost | Effect |
| --- | --- | --- |
| Strike | action | Finesse or ranged attack using Accuracy vs Avoidance. |
| Hide | bonus action by feature | Agility or stealth check against enemy awareness. Grants Hidden or Invisible pressure. |
| Skirmish | bonus action, 1 Edge | Move without triggering one reaction or gain Mobile stance until next turn. |
| Feint | bonus action | Presence or Agility check. On success, target becomes Reeling 1 or grants `+1` Accuracy to next attack. |
| Dirty Trick | action | Blind, distract, trip, disarm, or expose gear by tool and scene. |
| Tool Read | bonus action | Identify locks, traps, weak armor seams, poison vulnerability, or escape routes. |
| Exploit | rider | Extra damage or rider when the target is exposed. |
| Slip Away | reaction, 1 Edge | Add `+2` Avoidance against one attack after the roll is seen but before damage. |

### Exposed Targets

Many Rogue abilities care about exposed enemies.

An enemy is exposed if one or more are true:

- the Rogue is Hidden from it
- the enemy is Marked, Prone, Restrained, Reeling, Blinded, Poisoned, or Armor Broken
- the enemy is isolated from allies
- an ally is adjacent and threatening it
- Tool Read revealed a weakness this round
- the enemy missed the Rogue this round

### Shared Rogue Stances

| Stance | Effect | Notes |
| --- | --- | --- |
| Mobile | `+2` Avoidance, `-1` Accuracy | default skirmish stance |
| Hidden | attackers need awareness; Rogue gains first-strike pressure | requires cover, darkness, smoke, or misdirection |
| Low Guard | `+1` Avoidance, `+1` Stability against shove, no ranged attacks | alley fighting |
| Aggressive | `+2` Accuracy, `-1` Avoidance | finishers and risky burst |
| Patient | no movement; next Tool Read or attack gains `+1` | ambush setup |

### Shared Passive Tags

| Passive | Effect |
| --- | --- |
| Soft Step | First Hide attempt each combat gains `+1`. |
| Alley Sense | Gain `+1` initiative in cramped, urban, dungeon, or cluttered scenes. |
| Light Kit | Tool Read can be used as a bonus action. |
| Quick Hands | Use a small item, vial, or tool as a bonus action once per round. |
| Near Miss | Gain Edge when an attack misses you by 4 or less. |
| Seam Finder | Attacks against Armor Broken targets deal `+1` damage. |
| Smoke Memory | Smoke, darkness, or dust grants an additional `+1` Hide. |
| Poison Nerve | `+1` Endurance Resist Check against poison and toxins. |

## Level Progression

| Level | Rogue progression |
| ---: | --- |
| 1 | Choose Rogue. Gain Strike, Hide, Tool Read, one tool kit, and one Tier 1 technique. |
| 2 | Choose one Tier 1 technique or passive. Gain Edge and Skirmish. |
| 3 | Choose Shadowguard, Alchemist, Assassin, or Poisoner. Gain signature feature and one subclass technique. |
| 4 | Choose class or subclass technique. Choose stat increase or feat. |
| 5 | Power spike: gain Exploit upgrade or an archetype equivalent. Upgrade one known technique. |
| 6 | Choose utility technique and passive. Unlock improved stances. |
| 7 | Choose subclass specialization path. |
| 8 | Choose any known-tier technique. Choose stat increase or feat. |
| 9 | Gain advanced technique. Master one existing technique. |
| 10 | Choose capstone. Gain final archetype passive. |

### Exploit

At level 5, most Rogues gain Exploit: once per turn when hitting an exposed target, add bonus damage or a rider.

| Archetype | Level 5 spike |
| --- | --- |
| Shadowguard | Exploit can create a decoy or defensive swap. |
| Alchemist | Exploit can deliver a vial rider. |
| Assassin | Exploit adds execution damage. |
| Poisoner | Exploit adds poison stacks or detonates them. |

## Archetype 1: Shadowguard

### Combat Read

Shadowguards are avoidance tanks. They protect allies by making target priority unreliable. Decoys, smoke, taunts, swaps, and near misses turn enemy turns into wasted motion.

The Shadowguard tanks like a rumor in a knife fight. Everyone swings at the place they thought the rogue was standing.

### Role

| Role axis | Shadowguard position |
| --- | --- |
| Party role | Tank |
| Damage style | light counterattacks, mark punishment, decoy bursts |
| Protection style | evasion, misdirection, decoy, ally swap |
| Preferred armor | clothing, light armor, dark coats |
| Preferred weapons | daggers, short blades, bucklers if allowed, throwing knives |
| Primary stats | Agility, Instinct |
| Secondary stats | Presence, Reason |
| Weak points | area effects, true sight, high awareness enemies, unavoidable damage |

### Resource: Shadow

Shadow measures misdirection momentum.

```text
Shadow cap = 5
Gain 1 Shadow when an enemy misses you
Gain 1 Shadow when a decoy absorbs or redirects an attack
Gain 1 Shadow when you successfully Hide or Feint in combat
Spend Shadow on swaps, decoys, counterattacks, and ally protection
Shadow fades in bright open areas unless sustained by movement or smoke
```

### Signature Feature: False Target

Create a False Target adjacent to self or an ally for `1` round.

Effects:

- first enemy attack against the protected character has Snag or `-2` Accuracy
- if the attack misses, gain `1` Shadow
- on a near miss, the Shadowguard can move one step or apply Reeling 1

### Shadowguard Techniques

| Technique | Tier | Cost | Effect |
| --- | ---: | --- | --- |
| False Target | signature | bonus action, 1 Edge | Create decoy pressure around self or ally. |
| Slip Away | 1 | reaction, 1 Edge | Add `+2` Avoidance against one attack. |
| Smoke Pin | 1 | action, tool use | Create smoke or dust. Area grants Hide opportunities and lowers ranged Accuracy. |
| Cut The Eye | 1 | action | Attack. On Wound, target suffers `-1` awareness against Hide until next turn. |
| Near Miss | 1 | passive | Gain Edge when enemy misses you by 4 or less. |
| Wrong Foot | 2 | reaction, 1 Shadow | When an enemy misses, move it or yourself one step if terrain allows. |
| Cover The Healer | 2 | bonus action, 2 Shadow | Protected ally gains False Target and `+1` Avoidance until next turn. |
| Laugh From Elsewhere | 2 | Presence check | Apply Fixated to an enemy, but attacks against you have Snag if you are Hidden or in smoke. |
| Mirror Step | 2 | 2 Edge | Swap places with adjacent ally before an incoming melee attack resolves. |
| Knife In The Miss | 3 | reaction, 2 Shadow | Counterattack after an enemy misses you by 5 or more. |
| Vanish The Line | 3 | action, 3 Shadow | All allies in a smoke or shadow lane gain `+1` Avoidance until next turn. |
| Nobody There | 3 | passive | First attack against you each combat cannot benefit from Marked. |
| Shadow Snare | 4 | action, 4 Shadow | Decoy field. Enemies attacking protected allies risk Reeling or wasted attacks. |
| Bright Room Habit | 4 | passive | Shadow no longer fades in bright areas if you moved this round. |
| Empty Coat Miracle | capstone | 5 Shadow, reaction | When an ally would drop to `0`, swap them with a False Target. The hit destroys the decoy and the ally moves to safety at `1` HP. |

### Shadowguard Specialization Paths

| Path | Focus | Features |
| --- | --- | --- |
| Decoy Artist | false targets | stronger decoys, group concealment |
| Alley Saint | ally protection | swaps, cover, emergency saves |
| Knife Mirage | counterattacks | near-miss damage, Fixated tricks |

### Shadowguard Upgrade Examples

| Base technique | Upgrade | Effect |
| --- | --- | --- |
| False Target | Better Coat | Decoy can absorb one low-damage hit outright. |
| Slip Away | Thread The Needle | If the attack misses, gain `1` Shadow. |
| Smoke Pin | Ground Glass | Enemies inside also take `-1` awareness. |
| Mirror Step | Kindly Lie | The protected ally gains Guarded 1 after the swap. |
| Empty Coat Miracle | No One Saw Which Door | Ally also clears Marked or Fixated. |

### Shadowguard Combat Loop

1. Create smoke, cover, or a False Target.
2. Invite attacks into poor odds.
3. Gain Shadow from misses and decoy triggers.
4. Spend Shadow to protect allies or punish wasted attacks.
5. Stay mobile so area effects and awareness checks do not pin the rogue down.

### Shadowguard Tuning Notes

- Their tanking should reduce enemy efficiency, not absorb every hit.
- Area effects and save-based attacks should challenge them.
- Decoys need clear UI so the player sees which ally is protected.
- They should protect one or two allies well, then struggle if the whole party is scattered.

## Archetype 2: Alchemist

### Combat Read

Alchemists are tool healers. They throw restoratives, smoke jars, acids, oils, quick-stitch foam, and unstable brews. They heal through inventory-like choices and turn terrain into a problem for enemies.

Their kit should feel handmade. Cork teeth marks. Wax labels gone soft from body heat. One vial smells like mint and old coins, another like lamp oil and bad decisions.

### Role

| Role axis | Alchemist position |
| --- | --- |
| Party role | Heal |
| Damage style | vials, acid, fire oil, splash zones |
| Healing style | thrown healing, zones, buffs, condition treatments |
| Preferred armor | clothing, light armor, satchel harness |
| Preferred weapons | daggers, slings, hand crossbows, thrown vials |
| Primary stats | Reason, Agility |
| Secondary stats | Instinct, Endurance |
| Weak points | preparation limits, resistant enemies, running out of satchel charges, melee lockdown |

### Resource: Satchel

Satchel tracks prepared combat mixtures.

```text
Satchel cap = 6 + training bonus
Start combat with Satchel full after rest or preparation
Spend Satchel on thrown mixtures, emergency treatments, oils, bombs, and utility brews
Regain 1 Satchel after combat if supplies are available and the Alchemist had time to scavenge
Some rare ingredients create enhanced charges
```

Satchel can use existing item logic later, but the class should work without counting every bottle.

### Secondary Resource: Reaction

Alchemist mixtures can leave Reaction tags on targets or terrain.

| Reaction tag | Trigger |
| --- | --- |
| Oiled | fire spreads, slip risk, weapon grip penalty |
| Dosed | healing and poison interactions improve |
| Acid-Etched | Defense reduction or Armor Break risk |
| Smoked | Hide and ranged penalties |
| Numbed | reduced damage or delayed pain |
| Catalyzed | next mixture has stronger effect |

### Signature Feature: Quick Mix

As a bonus action, prepare one mixture tag. The next Alchemist vial this turn gains that tag's rider.

Examples:

- Healing + Numbed: heal and grant temporary HP
- Smoke + Oiled: concealment and slip risk
- Acid + Catalyzed: stronger Defense reduction
- Tonic + Dosed: condition clear with small heal

### Alchemist Techniques

| Technique | Tier | Cost | Effect |
| --- | ---: | --- | --- |
| Quick Mix | signature | bonus action | Add a rider to the next mixture this turn. |
| Redcap Tonic | 1 | action, 1 Satchel | Heal ally for `1d6 + Reason modifier`; range by throw. |
| Smoke Jar | 1 | action, 1 Satchel | Create smoke zone. Allies can Hide; ranged attacks take penalty. |
| Bitter Acid | 1 | action, 1 Satchel | Acid attack. On failed Resist Check, reduce Defense by `10 percentage points` for one round. |
| Field Stitch | 1 | action, 1 Satchel | Stop Bleeding or stabilize ally at `0` HP. |
| Fast Cork | 1 | passive | Once per round, draw a vial without spending the small-item action. |
| Flash Powder | 2 | action, 1 Satchel | Blinding burst. Targets make Agility or Endurance Resist Check. |
| Nerve Salt | 2 | bonus action, 1 Satchel | Ally clears Reeling or gains `+1` Accuracy for next attack. |
| Oil Slick | 2 | action, 1 Satchel | Terrain zone. Enemies risk Prone; fire channels interact. |
| Shared Dose | 2 | 1 Edge | A healing vial splashes a second adjacent ally for half healing. |
| Catalytic Throw | 3 | action, 2 Satchel | Mixture against a Reaction-tagged target gains stronger effect. |
| White Foam | 3 | reaction, 2 Satchel | Reduce incoming fire, acid, or poison damage and grant brief resistance. |
| Walking Cabinet | 3 | passive | Satchel cap increases by `2`; regain one extra charge after long rest. |
| Bad Bottle | 4 | action, 3 Satchel | Unstable area vial. Damage, Reeling, and Reaction tags by chosen mix. |
| Clean Label Method | 4 | passive | First Quick Mix each combat refunds `1` Satchel if it heals or clears a condition. |
| Whole Satchel Trick | capstone | 5 Satchel | Throw a chain of three mixtures: one healing, one control, one damage. Each must target a different point or character. |

### Alchemist Specialization Paths

| Path | Focus | Features |
| --- | --- | --- |
| Field Medic | healing and condition clear | stronger tonics, faster stabilizes |
| Bombhand | control and damage | acid, smoke, oil, flash, explosions |
| Reagent Savant | reactions | mix chains, enhanced ingredients, resource refunds |

### Alchemist Upgrade Examples

| Base technique | Upgrade | Effect |
| --- | --- | --- |
| Redcap Tonic | Warm Bite | Heal also grants `+1` Endurance Resist Check. |
| Smoke Jar | Black Wool | Smoke lasts one extra round in enclosed spaces. |
| Bitter Acid | Buckle-Eater | Strong failure applies Armor Break 1. |
| Field Stitch | Quick Needle | Can be used as bonus action on adjacent ally. |
| Whole Satchel Trick | Every Cork At Once | One mixture can be duplicated at half strength. |

### Alchemist Combat Loop

1. Read the party's injuries and the room.
2. Use Quick Mix to prepare the right rider.
3. Throw healing, smoke, acid, or oil where it changes tempo.
4. Build Reaction tags.
5. Spend Satchel hard during dangerous rounds, then recover through rests and scavenging.

### Alchemist Tuning Notes

- Alchemist healing should be more flexible than Aethermancer healing, with tighter resource pressure.
- Mixture zones should support Shadowguard, Poisoner, and Elementalist play.
- The class needs clear labels in UI so combinations do not become memory work.
- Satchel recovery should depend on supplies, but ordinary fights should avoid punishing experimentation too heavily.

## Archetype 3: Assassin

### Combat Read

Assassins are single-target eliminators. They use stealth, isolation, marks, and execution windows to remove dangerous enemies before the fight becomes fair.

Their damage should feel exact. No flourish, no speech. The target reaches for the horn and finds the hand no longer answers cleanly.

### Role

| Role axis | Assassin position |
| --- | --- |
| Party role | DPS |
| Damage style | burst, execute, opener pressure |
| Protection style | stealth, mobility, target removal |
| Preferred armor | clothing, light armor |
| Preferred weapons | daggers, stilettos, short bows, garrotes, hand crossbows |
| Primary stats | Agility |
| Secondary stats | Instinct, Reason |
| Weak points | alert enemies, swarms, heavy armor, true sight, long boss fights |

### Resource: Mark

Mark tracks the Assassin's chosen victim.

```text
One active Death Mark at a time
Apply Death Mark through Tool Read, Hidden attack, or bonus action setup
Gain 1 Edge when the marked target becomes isolated, Reeling, Prone, Poisoned, or Armor Broken
Spend Edge to improve attacks against marked target
Mark ends when target dies, combat ends, or Assassin marks someone else
```

### Signature Feature: Death Mark

Mark one target you can see or have successfully tracked. The Assassin gains `+1` Accuracy against that target while Hidden or while the target is exposed.

First Wound against Death Mark each combat adds execution damage.

### Assassin Techniques

| Technique | Tier | Cost | Effect |
| --- | ---: | --- | --- |
| Death Mark | signature | bonus action | Mark target for accuracy and execution riders. |
| Quiet Knife | 1 | action | Attack from Hidden. On hit, add bonus damage and stay Hidden on strong hit. |
| Low Shot | 1 | action | Ranged attack. On Wound, reduce target movement. |
| Cut The Strap | 1 | action | Attack armor seam. On strong hit, apply Armor Break 1. |
| Vanishing Habit | 1 | passive | After dropping a target, Hide as a free reaction if cover exists. |
| Isolate | 2 | bonus action, 1 Edge | Target loses benefit from nearby allies until next turn if it fails Instinct Resist Check. |
| Between Plates | 2 | 2 Edge | Next attack against Death Mark ignores `10 percentage points` of Defense. |
| No Witness Angle | 2 | passive | Gain `+1` Accuracy against isolated targets. |
| Throat Count | 2 | Tool Read | Identify whether target is vulnerable to bleed, poison, armor seam, or fear. |
| Sudden End | 3 | action, 3 Edge | Execute attack. Extra damage if target is below half HP or isolated. |
| Gone Before The Body Falls | 3 | reaction, 2 Edge | After dropping Death Mark, move and Hide if possible. |
| Kill The Signal | 3 | action | Attack a caster, horn-blower, commander, or relay target. On Wound, interrupt one support effect. |
| Red Window | 4 | passive | First round of combat, Death Mark starts with exposed status if the party was not Surprised. |
| Hand On The Candle | 4 | reaction, 3 Edge | When Death Mark tries to heal, flee, or command, make an interrupting attack. |
| One Name Crossed Out | capstone | 5 Edge | Against Death Mark, make a high-precision attack. If target is below half HP, double execution rider; if it dies, regain Edge and mark another target. |

### Assassin Specialization Paths

| Path | Focus | Features |
| --- | --- | --- |
| Red Knife | melee burst | armor seams, bleed, vanish on kill |
| Rooftop Hand | ranged execution | marked shots, movement denial |
| Silence Broker | support removal | interrupts, commander pressure, anti-caster tools |

### Assassin Upgrade Examples

| Base technique | Upgrade | Effect |
| --- | --- | --- |
| Death Mark | Private Name | Mark does not break Hidden if applied from concealment. |
| Quiet Knife | No Cloth Sound | On kill, nearby enemies take awareness penalty for one round. |
| Cut The Strap | Buckle Gone | Armor Break lasts one extra round if attack came from Hidden. |
| Sudden End | Mercy Of Speed | Refund `1` Edge if target drops. |
| One Name Crossed Out | Second Line Ready | If capstone kills, next Death Mark costs no bonus action. |

### Assassin Combat Loop

1. Identify the enemy that warps the fight.
2. Apply Death Mark before full exposure.
3. Create isolation through movement, ally pressure, smoke, or control.
4. Strike from Hidden or into an exposed condition.
5. Spend Edge on Defense ignore, execute damage, or a vanish reset.

### Assassin Tuning Notes

- Assassin burst should be scary, then taper if the target survives.
- Heavy Defense targets need seams, Armor Break, poison, or ally setup.
- Bosses should resist instant deletion through phase gates, high awareness, or mark cleansing.
- The opening round should be meaningful without ending every important fight.

## Archetype 4: Poisoner

### Combat Read

Poisoners are attrition controllers. They apply stacks, weaken Resist Checks, punish healing, and detonate toxins when the target tries to recover. Their damage starts quiet and becomes a schedule the enemy cannot keep.

The Poisoner notices cups, gloves, breath, sweat, and impatience. The blade is delivery. The waiting does the work.

### Role

| Role axis | Poisoner position |
| --- | --- |
| Party role | DPS |
| Damage style | stacking damage over time, debuffs, delayed burst |
| Protection style | range, slows, weakness, smoke, antidotes |
| Preferred armor | clothing, light armor |
| Preferred weapons | daggers, darts, blowpipes, needles, short bows |
| Primary stats | Reason, Agility |
| Secondary stats | Instinct, Endurance |
| Weak points | poison immune enemies, high Endurance saves, short fights, clean armor with no Wound |

### Resource: Toxin

Toxin tracks prepared poisons and applied stacks.

```text
Toxin prep cap = 5 + training bonus
Spend prep to coat weapons, throw clouds, lace terrain, or brew antidotes
Poison stacks on enemies cap at 5 by default
Stacks usually require a Wound, failed Endurance Resist Check, inhaled cloud, or exposed food/water scene
Poison stacks tick at end of enemy turn
Stacks fade by 1 each round unless refreshed or stabilized by feature
```

### Poison Lanes

| Lane | Effect |
| --- | --- |
| Venom | HP damage over time after Wound or failed Endurance Resist Check |
| Nerve | Reeling, Accuracy loss, reaction loss |
| Rot | healing reduction, Defense corrosion if acid-carrier |
| Sleep | awareness loss, action pressure, nonlethal takedown |
| Panic | fear, Presence pressure, target misreads |
| Antidote | clears poison, grants brief resistance, can be weaponized against toxins |

### Signature Feature: Black Drop

Coat a weapon or dart with Black Drop. The next Wound forces an Endurance Resist Check. On failure, apply Poison 2. On success, apply Poison 1.

If the attack is a Glance, Black Drop remains on the weapon unless the target's armor is sealed or the weapon was blocked by a shield.

### Poisoner Techniques

| Technique | Tier | Cost | Effect |
| --- | ---: | --- | --- |
| Black Drop | signature | bonus action, 1 Toxin | Weapon coating that applies Poison stacks on Wound or save. |
| Green Needle | 1 | action | Ranged finesse attack. On Wound, apply Poison 1. |
| Bitter Cloud | 1 | action, 1 Toxin | Small inhaled zone. Endurance Resist Check or Poisoned/Reeling. |
| Antidote Pin | 1 | action, 1 Toxin | Clear Poisoned or grant `+1` Endurance Resist Check to ally. |
| Slow Measure | 1 | passive | Poison stacks fade slower on targets you hit this round. |
| Nerve Lace | 2 | 1 Toxin | Poison lane changes to Reeling and reaction loss rather than raw damage. |
| Rot Thread | 2 | 1 Toxin | Poison lane reduces healing received and can corrode Defense on failed save. |
| Taste For Weakness | 2 | Tool Read | Reveal poison resistance, immunity, lowest save, and whether target needs Wound delivery. |
| Dose The Edge | 2 | 1 Edge | If an exposed target is hit, apply one extra poison stack. |
| Bloom In The Blood | 3 | action, 2 Toxin | Detonate poison stacks for burst damage. Clears some stacks after damage. |
| Patient Poison | 3 | passive | Poison stacks on Death Mark, Red Mark, or Marked targets last one extra round. |
| Bad Antidote | 3 | reaction, 2 Toxin | When poisoned enemy heals, reduce the healing and apply Reeling 1. |
| Room Dose | 4 | action, 3 Toxin | Larger zone. Enemies make Endurance Resist Check each round inside. Allies with antidote ignore first tick. |
| Clean Hands | 4 | passive | Once per combat, applying poison does not break Hidden. |
| The Last Taste | capstone | 5 Toxin | Choose one poisoned target. Convert all stacks into a major effect by lane: damage, sleep, panic, heal lock, or Defense corrosion. |

### Poisoner Specialization Paths

| Path | Focus | Features |
| --- | --- | --- |
| Venomist | raw poison damage | higher stacks, stronger detonation |
| Nerve-Cutter | control | Reeling, action denial, reaction disruption |
| Apothecary | antidote and support | ally protection, anti-poison, flexible lanes |
| Rot-Hand | corrosion and heal denial | Armor Break, anti-heal, acid carriers |

### Poisoner Upgrade Examples

| Base technique | Upgrade | Effect |
| --- | --- | --- |
| Black Drop | Sticks To The Seam | Glances against Armor Broken targets still deliver Poison 1. |
| Bitter Cloud | Low Vapor | Cloud hugs ground and is harder to disperse indoors. |
| Antidote Pin | Warm Vein | Also heals `1d4` if target had Poisoned. |
| Bloom In The Blood | Red Flower | Detonation leaves Poison 1 behind. |
| The Last Taste | No Bitter Face | If the target drops, nearby enemies do not immediately identify the Poisoner. |

### Poisoner Combat Loop

1. Read resistance and delivery needs.
2. Apply the right poison lane.
3. Use exposed attacks, clouds, or ally marks to build stacks.
4. Keep stacks from fading through pressure.
5. Detonate when the target is near a heal, phase change, or dangerous turn.

### Poisoner Tuning Notes

- Poisoner should outperform burst classes in long fights.
- Poison immunity needs alternate lanes: acid, smoke, antidote support, or panic toxins.
- Stacks must be visible in UI and easy to predict.
- Wound-gated delivery makes Defense matter; clouds and inhaled effects offer a slower workaround.

## Rogue Ability Tiers

### Tier 1: Levels 1-3

| Ability | Archetype | Use |
| --- | --- | --- |
| False Target | Shadowguard | defensive misdirection |
| Redcap Tonic | Alchemist | thrown healing |
| Death Mark | Assassin | target selection |
| Black Drop | Poisoner | poison delivery |
| Tool Read | shared | identify weakness |
| Slip Away | shared | reactive Avoidance |

### Tier 2: Levels 3-6

| Ability | Archetype | Use |
| --- | --- | --- |
| Mirror Step | Shadowguard | ally swap |
| Flash Powder | Alchemist | control and Hide support |
| Between Plates | Assassin | Defense ignore |
| Nerve Lace | Poisoner | control poison |

### Tier 3: Levels 5-8

| Ability | Archetype | Use |
| --- | --- | --- |
| Knife In The Miss | Shadowguard | counterattack |
| Catalytic Throw | Alchemist | reaction-tag payoff |
| Sudden End | Assassin | execute |
| Bloom In The Blood | Poisoner | poison detonation |

### Tier 4: Levels 9-10

| Ability | Archetype | Use |
| --- | --- | --- |
| Empty Coat Miracle | Shadowguard | decoy rescue |
| Whole Satchel Trick | Alchemist | mixed chain turn |
| One Name Crossed Out | Assassin | death mark climax |
| The Last Taste | Poisoner | stack conversion |

## Feat Ideas For Rogues

| Feat | Effect |
| --- | --- |
| Knife Weather | Throwing weapons gain `+1` Accuracy from Hidden or smoke. |
| Alley Vanish | First move into cover each combat can trigger Hide. |
| Soft Hands | Tool Read and small item use can share one bonus action once per combat. |
| Dirty Practical | Dirty Trick gains `+1` against enemies already Reeling or Prone. |
| Poison Nerve | Resist poison with Edge once per combat. |
| False Badge | Social combat feints can create exposed status before combat starts. |
| Quick Cork | Alchemist or item-user can use a small vial as reaction once per combat. |
| Seam Killer | First hit against Armor Broken target each combat adds extra damage. |

## Equipment Hooks

| Item trait | Rogue interaction |
| --- | --- |
| Concealable | Can be drawn while Hidden without breaking stealth. |
| Silent | Hide checks avoid one noise penalty. |
| Serrated | Bleeding rider on Wound. |
| Hollow | Can carry one poison or alchemical dose. |
| Blackened | Reduces reveal chance in darkness or soot. |
| Quick-Corked | Vial can be thrown as bonus action with Quick Hands. |
| Smoke-Oil | Creates smoke and Oiled terrain when broken. |
| Seam-Finder | `+1` Accuracy against Armor Broken or high-Defense targets. |

## Party Synergies

| Partner style | Rogue synergy |
| --- | --- |
| Juggernaut | Fixated enemies expose backs and waste attacks into decoys |
| Bloodreaver | Red Mark rewards Rogue focus fire and poison pressure |
| Berserker | Berserker chaos creates isolated, Reeling, and Prone targets |
| Weapon Master | Weapon Read identifies seams for Assassin and Poisoner |
| Spellguard | Wards keep low-Defense Rogues alive during setup |
| Aethermancer | field healing supports risky flanks |
| Arcanist | Pattern Charge and Death Mark can focus the same priority target |
| Elementalist | smoke, oil, frost, and acid fields combine with Rogue tools |

## Enemy Counters

| Counter | Best against | Why |
| --- | --- | --- |
| Area effects | Shadowguard, Assassin | bypass single-target Avoidance and decoys |
| True sight or high awareness | Shadowguard, Assassin | weakens Hide and False Target |
| Poison immunity | Poisoner | blocks primary stack lane |
| Heavy Defense | Assassin, Poisoner | prevents Wound delivery |
| Cleanse effects | Poisoner, Assassin | removes stacks or marks |
| Rushdown grapplers | Alchemist, Assassin | locks down range and tools |
| Scatter AI | Alchemist, Poisoner | reduces zones and clouds |
| Long attrition | Assassin | burst fades if reset fails |

## UI Presentation

Rogue turns should show position and tempo.

```text
Kaelis - HP 22/28 - Defense 10% - Avoidance +5 - Edge 3 - Stance: Mobile - Hidden
Shadowguard: Shadow 2, False Target on Elira
Alchemist: Satchel 5, prepared rider Numbed
Assassin: Death Mark on Ashen Captain
Poisoner: Black Drop armed, Poison stacks 3
```

Resolution text should show the cause of advantage.

```text
The spear misses by a breath. Near Miss grants Edge.
False Target takes the captain's attention; the healer is already behind the crate with chalk on one sleeve.
Black Drop catches under the glove seam. Endurance fails. Poison 2.
Redcap Tonic lands hard against Rhogar's shoulder and the numbness follows the heat.
```

## Implementation Notes

Recommended first Rogue slice:

1. Implement Edge as a small per-combat resource.
2. Add Hide, exposed target checks, and Tool Read labels.
3. Implement Shadowguard False Target because it tests Avoidance tanking.
4. Implement Alchemist Satchel with Redcap Tonic, Smoke Jar, Bitter Acid, and Quick Mix.
5. Implement Assassin Death Mark after exposed target checks are reliable.
6. Implement Poisoner after Wound-only delivery and stack UI exist.
7. Add equipment traits after tool and vial actions feel stable.

## Open Design Questions

- Should Edge be gained from every near miss or only once per round?
- Should Hide use map positions, abstract cover states, or both?
- Should Shadowguard decoys be targetable entities or status effects on allies?
- Should Alchemist Satchel consume actual inventory items or a class resource?
- Should Assassin burst be capped against bosses by phase, resistance, or mark stacks?
- Should Poison stacks require Wounds by default, or should inhaled and contact lanes be common?
- Should Tool Read reveal exact values or simple labels like `high Defense` and `weak Endurance`?
