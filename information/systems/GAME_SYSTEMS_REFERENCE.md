# Aethrune Systems Reference

This file is a source-oriented reference for reading and debugging the current game implementation.

## Scope

- Current fully playable campaign scope: Act 1
- Current playable scaffold: Act 2 route framework, claims council, expedition hub, local-map slices, and Act 3 handoff flags
- Current level cap: 4
- Party progression is shared across the whole company
- The terminal UI supports Rich panels for interactive play and plain-safe output for pipes, scripted input, and smoke tests.
- The game uses a compact SRD-derived d20 rules layer internally while public terminology is being moved toward Aethrune.

## Source Map

- `dnd_game/game.py`: main composed game class
- `main.py`: CLI entry point and smoke-test flags
- `dnd_game/gameplay/creation.py`: character creation flow
- `dnd_game/gameplay/io.py`: prompt rendering, Rich/plain fallback, command shelf, non-interactive safeguards, and save manager UI
- `dnd_game/gameplay/journal.py`: decision ledger, clue log, faction pressure, and companion disposition summary
- `dnd_game/gameplay/companions.py`: companion recruitment, trust changes, assists, camp counsel, and refusal hooks
- `dnd_game/gameplay/camp.py`: rest flow, camp actions, companion talks, and camp banter entry points
- `dnd_game/data/story/character_options/classes.py`: classes and level progression
- `dnd_game/data/story/character_options/races.py`: races
- `dnd_game/data/story/character_options/backgrounds.py`: backgrounds
- `dnd_game/gameplay/progression.py`: XP and level-up handling
- `dnd_game/gameplay/map_system.py`: live Act 1 and Act 2 map flow, route flags, reactivity state, and epilogue carryover
- `dnd_game/gameplay/magic_points.py`: MP formulas, spell costs, spend/restore helpers, and spell-slot-to-MP item conversion
- `dnd_game/gameplay/combat_flow.py`: combat turn options and enemy AI
- `dnd_game/gameplay/combat_resolution.py`: attack, spell, healing, damage, save, and death logic
- `dnd_game/gameplay/status_effects.py`: status definitions and condition ticking
- `dnd_game/gameplay/inventory_core.py`: resting, supply use, loot, item use
- `dnd_game/gameplay/random_encounters.py`: post-combat event pool, follow-up chains, and Act-specific encounter tables
- `dnd_game/data/story/factories.py`: hero and enemy factory data
- `dnd_game/data/quests/act1.py`: quest definitions
- `information/systems/QUEST_SYSTEM_REFERENCE.md`: detailed quest lifecycle, rewards, turn-in, and maintenance reference
- `information/catalogs/ITEM_CATALOG.md`: generated item and equipment catalog
- `tools/prose_lint.py`: public-facing prose lint for banned patterns and legacy names
- `tools/sync_android_port.py`: desktop-to-Android drift checker and sync helper

## Terminal, CLI, And Saves

### Non-interactive safety

- `--plain` forces plain output.
- `--no-animation` disables typed narration, dice pacing, and other wait-heavy presentation.
- `--no-audio` skips audio setup and playback.
- `--load-save SLOT` loads a save slot at startup.
- `--scripted-input FILE` reads prompt answers from a text file.
- When stdin or stdout is piped, `io.py` disables Rich live menus, keyboard polling, box drawing, animations, and resize-aware rendering.

### Prompt commands

- Choice prompts show a small command shelf under the scene text.
- Exploration shelves include `map`, `journal`, `party`, `inventory`, `camp`, `save`, and `settings` when each command is currently available.
- Combat shelves omit unavailable commands such as `map` and `camp`.
- Global commands still work at ordinary prompts, even when a scene has temporarily disabled meta-menu interruptions for the choice itself.
- The help menu is grouped by use and keeps `quit` last.
- The developer console uses a Rich table in interactive mode and grouped plain text in non-interactive mode.

### Save previews

- Save rows show compact metadata: autosave/manual state, slot or label, act, scene, party level, and playtime.
- The current objective stays available in the detail view so the save list remains short.
- Metadata is derived during save writes and reconciled when old saves are loaded.

### Android mirror drift

- Desktop `dnd_game/` is the shared source.
- `python tools\sync_android_port.py` reports drift against `android_port/dnd_game/`.
- `python tools\sync_android_port.py --apply` copies changed and missing shared files into the Android mirror.
- Stale Android-only files still need hand review before deletion.

## Campaign State Layers

### Act 1 route structure

- Overworld travel is node-based around the save-safe `iron_hollow_hub` id, now presented as Iron Hollow.
- Hostile sites use room-based dungeon progression from `dnd_game/drafts/map_system/data/act1_hybrid_map.py`
- The live mid-Act route can now include Blackglass Well, Red Mesa Hold, and an optional hidden Cinderfall Ruins strike before Ashfall Watch.
- The Emberway now has a post-ambush travel choice before Iron Hollow. Once both ambush waves are cleared, the scene reopens with the south road, a `BACKTRACK` option when history allows it, and any unlocked side branches: `Liar's Circle`, `False Roadwarden Checkpoint`, and `False Tollstones`.
- Returning from those Emberway side branches travels to `iron_hollow_hub` without recording the side branch as the new backtrack target. From Iron Hollow, backtracking skips resolved Emberway side detours and points back to the meaningful route node.

### Act 1 metrics and carryover

- `act1_town_fear`
  - default `2`
  - tracks how badly Iron Hollow is rattled
- `act1_ashen_strength`
  - default `3`
  - tracks how much outer-site pressure the Ashen Brand still retains
- `act1_survivors_saved`
  - default `0`
  - tracks rescue outcomes across the act
- `act1_victory_tier`
  - recorded as `clean_victory`, `costly_victory`, or `fractured_victory`
- `act2_starting_pressure`
  - derived from the ending tier plus a few late moral choices such as selling Bryn's ledger

### Quest-state rules

- Quest log statuses are `active`, `ready_to_turn_in`, and `completed`
- Readiness is driven from flags, not scene position alone
- Some Act 1 quests are auto-granted from companion trust thresholds rather than a town-giver menu

## Journal And Decision Ledger

- `journal.py` presents the journal as a decision ledger instead of a simple quest list.
- Major choices appear with their current consequences when flags or metrics expose a result.
- Faction pressure entries summarize route control, civic fear, Act 2 pressure, and related campaign metrics.
- Companion entries show disposition, recent trust changes, unlocked support, and refusal risk.
- Unresolved clues remain visible until the campaign records a resolved flag or follow-up state.

## Companion Trust Mechanics

- Companion profiles define trust events, assist skills, camp counsel, and combat opener data.
- Disposition `6+` can unlock skill-check assists, trusted camp counsel, and encounter openers.
- Disposition `9+` can strengthen some trusted-support outcomes.
- Disposition `-3` or lower can create social-check tension and withhold support.
- Very low trust can trigger active-party refusal or altered quest outcomes when a companion's values are directly crossed.

## Character Creation

### Ability assignment

- Standard array: `15, 14, 13, 12, 10, 8`
- Point buy budget: `27`
- Point buy costs:

| Score | Cost |
| --- | ---: |
| 8 | 0 |
| 9 | 1 |
| 10 | 2 |
| 11 | 3 |
| 12 | 4 |
| 13 | 5 |
| 14 | 7 |
| 15 | 9 |

### Shared character formulas

- Ability modifier: `(score - 10) // 2`
- Proficiency bonus: `2 + max(0, (level - 1) // 4)`
- Levels 1-4 all currently use proficiency bonus `+2`
- Starting HP: `hit die + CON modifier`, minimum `1`
- Unarmored AC:
  - default: `10 + DEX`
- Weapon attack bonus: attack ability modifier + proficiency + weapon bonus + bonuses from features, gear, and relationships
- Weapon damage bonus: attack ability modifier + weapon bonus + bonuses from features, gear, and relationships
- Spell attack bonus: proficiency + spellcasting ability modifier + spell attack bonuses
- Spell save DC: `8 + proficiency + spellcasting ability modifier`

### Magic Points

Combat spellcasting now uses Magic Points (`MP`) as the player-facing resource. Spell-slot resources still synchronize as compatibility data, but combat menus, party sheets, combatant summaries, rest recovery, and spell-refresh consumables all speak in MP.

- MP is stored as `resources["mp"]` with the maximum in `max_resources["mp"]`
- Mages: `6 + 4 * level + max(0, spellcasting modifier)`
- Feature-based channelers use `3 + max(0, spellcasting modifier)` when a future feature grants `magic_initiate` or `racial_magic`
- Characters without spellcasting or feature-caster access have no MP row
- Creation, level reconciliation, and old-save integrity checks call `synchronize_magic_points`
- Combat options only show spells the actor can currently afford; direct cast attempts with too little MP print the required cost and current MP

## Classes

| Class | HD | Saves | Level 1 features | Starting resources | Spell stat |
| --- | ---: | --- | --- | --- | --- |
| Warrior | d10 | STR, CON | Grit, Guard Stance, Shove, Pin, Rally, Weapon Read | grit 1 | none |
| Mage | d6 | INT, WIS | Charge, Focus, Minor Channel, Pattern Read, Ground, Focused Eye | MP by formula | INT |
| Rogue | d8 | DEX, INT | Veilstrike, Deep Practice, Edge, Mark Work, Satchel Kit, Poison Work | none | none |

## Leveling

### Shared XP thresholds

| Level | XP |
| --- | ---: |
| 1 | 0 |
| 2 | 300 |
| 3 | 900 |
| 4 | 2700 |

### Level-up rules

- XP is stored once on `GameState`, not per character
- Every party member and companion levels together when the shared XP threshold is reached
- HP gain on level-up: `max(1, hit_die // 2 + 1 + CON modifier)`
- The player picks one new class skill at each level-up if one remains available
- Companions auto-pick the first available class skill
- Mages resynchronize MP on level-up and save reconciliation; spell-slot values still synchronize as hidden compatibility data

### Class progression by level

#### Warrior

- Level 2: Hard Lesson; Grit maximum follows Endurance and training
- Level 3: Juggernaut Training, Line Holder, `+1 Stability`
- Level 4: Weapon Familiarity, Style Wheel, Berserker Training, Bloodreaver Training, `+1 attack`, `+1 damage`

#### Mage

- Level 2: Field Sense, Steady Hands, `+1 CON saves`
- Level 3: Counter-Cadence, `+1 WIS saves`
- Level 4: Channel Focus, Spellguard Training, Arcanist Training, Elementalist Training, Aethermancer Training, `+1 channel strike`

#### Rogue

- Level 2: Cunning Action, `+2 Stealth`, `+2 initiative`
- Level 3: Deadly Sneak Attack, Sneak Attack becomes `2d6`
- Level 4: Evasion, `+2 DEX saves`

## Races

| Public race (mechanics key) | Ability bonuses | Skill grants | Feature tags |
| --- | --- | --- | --- |
| Human | STR+1, DEX+1, CON+1, INT+1, WIS+1, CHA+1 | none | none |
| Dwarf | CON+2 | none | darkvision, dwarven_resilience |
| Elf | DEX+2 | Perception | darkvision, keen_senses, fey_ancestry |
| Halfling | DEX+2 | none | lucky, brave |
| Forged (`Dragonborn`) | STR+2, CHA+1 | none | draconic_presence |
| Unrecorded (`Gnome`) | INT+2 | Investigation | gnome_cunning |
| Astral Elf (`Half-Elf`) | CHA+2, DEX+1, WIS+1 | Insight, Persuasion | fey_ancestry |
| Orc-Blooded (`Half-Orc`) | STR+2, CON+1 | Intimidation | relentless_endurance, menacing |
| Fire-Blooded (`Tiefling`) | INT+1, CHA+2 | none | darkvision, hellish_resistance |
| Riverfolk (`Goliath`) | STR+2, CON+1 | Athletics | stone_endurance |
| Orc | STR+2, CON+1 | Intimidation | darkvision, adrenaline_rush |

### Racial feature hooks

Implemented directly in mechanics:

- `lucky`: rerolls natural 1s on d20 rolls
- `dwarven_resilience`: poison save advantage and poison resistance
- `hellish_resistance`: fire resistance
Present as tags and lore, but not given dedicated runtime logic yet:

- `darkvision`
- `keen_senses`
- `fey_ancestry`
- `brave`
- `draconic_presence`
- `gnome_cunning`
- `relentless_endurance`
- `menacing`
- `stone_endurance`
- `adrenaline_rush`

## Backgrounds

| Background | Skill proficiencies | Extra proficiencies | Passive bonuses |
| --- | --- | --- | --- |
| Soldier | Athletics, Intimidation | Land Vehicles, Gaming Set | Athletics +1, Intimidation +1 |
| Acolyte | Insight, Religion | Calligrapher's Supplies, Celestial | Medicine +1, Religion +1 |
| Criminal | Deception, Stealth | Thieves' Tools, Disguise Kit | Stealth +1, Sleight of Hand +1 |
| Sage | Arcana, History | Calligrapher's Supplies, Draconic | Arcana +1, History +1 |
| Outlander | Athletics, Survival | Herbalism Kit, One Musical Instrument | Nature +1, Survival +1 |
| Charlatan | Deception, Sleight of Hand | Forgery Kit, Disguise Kit | Deception +1, Performance +1 |
| Guild Artisan | Insight, Persuasion | Artisan's Tools, Merchant's Scales | History +1, Persuasion +1 |
| Hermit | Medicine, Religion | Herbalism Kit, Sylvan | Insight +1, Medicine +1 |

## Combat Flow

### Turn structure

- Each turn starts with `1` action and `1` bonus action
- Player combat options are grouped by `Action`, `Bonus Action`, `Item`, `Social`, `Escape`, and `End Turn`
- Display numbers remain sequential from top to bottom across the grouped menu
- Some abilities add or trade on top of that:
  - Warrior Rally uses a bonus action and Grit
  - Mage Pattern Read, Ground, Pulse Restore, and several ward tools use bonus actions
  - Rogue Cunning Action uses bonus action
  - Off-hand attack requires the Attack action first
- Dodge is a full action
- Trying to flee usually costs an action and uses Stealth vs DC `13`
- Free flee can be created by Cunning Action dash/disengage

### Initiative

- Initiative = d20 + DEX modifier + initiative bonuses + encounter hero/enemy bonus
- Tie sorting prefers higher DEX and then heroes over enemies

### Companion combat support

- Scene support bonuses are separate from combat-start openers
- Companion profiles can define `combat_opener` data rather than hard-coded opener branches
- At disposition `6+`, trusted companions can apply opener statuses or tactical pressure at encounter start
- Kaelis currently uses scout pressure through `Shadow Volley`
- Tolan currently uses shield-line pressure through `Hold the Line`
- Low-trust companions can withhold opener support

### Enemy coordination hooks

- `Marked` is now a shared focus-fire status
- `Ember Channeler` can apply `Marked 2`, and enemies with updated AI will prefer marked heroes when possible
- `Ashen Brand Enforcer` can spend `punishing_strike` to punish buffed or marked heroes and strip `Blessed`
- `Carrion Stalker` opens under `Invisible` pressure and applies `Bleeding` on hits

### Criticals

- Normal critical threshold: `20`
- Criticals double the dice count in the rolled expression

### Sneak Attack

- Rogue Sneak Attack is active if another conscious hero is present and the target is conscious
- It currently triggers on weapon attacks when the computed attack advantage state is not negative
- Damage:
  - Levels 1-2: `1d6`
  - Levels 3-4: `2d6`

### Off-hand rules

- Requires light melee weapons in both hands
- No ranged weapons
- No two-handed weapons
- Off-hand damage does not include positive ability modifier

## Implemented Spells And Active Combat Abilities

| Spell or ability | Users | Cost | Effect |
| --- | --- | --- | --- |
| Minor Channel | Mage | action, 1 MP | INT channel strike, `1d8` force, builds Focus on pressure |
| Arc Pulse | Mage | action, 1 MP | resist check for `1d8` force, adds Pattern Charge on a clean hit |
| Ember Lance | Mage | action, 1 MP | channel strike for fire damage and burning pressure |
| Frost Shard | Mage | action, 1 MP | channel strike for cold damage and slowing pressure |
| Volt Grasp | Mage | action, 1 MP | close channel strike with shock pressure |
| Field Mend | Mage | action, 3 MP | field healing using the Mage channel DC lane |
| Pulse Restore | Mage | bonus action, 4 MP | fast ally healing that leaves the action free |
| Warrior Rally | Warrior | bonus action, 1 Grit | clears Reeling or grants Guarded 1 |
| Cunning Action | Rogue level 2+ | bonus action | hide for Invisible 2 on success, or create a flee opening |
| Help a Downed Ally | any hero | action | Medicine check DC `10`; on success target returns at 1 HP, on failure target stabilizes |

### Spell timing rule

- Bonus-action channeling spends the bonus action; action channels remain available if the actor still has an action
- Expensive Mage channels are gated by MP and feature training

## Status Effects

| Status | Main effect |
| --- | --- |
| Surprised | loses turn once |
| Blinded | attack disadvantage, helps attackers hit, hurts some checks |
| Charmed | cannot make hostile actions |
| Deafened | hurts hearing-based Perception checks |
| Exhaustion | skill disadvantage at 1+, attack penalty at 2+, save disadvantage at 3+ |
| Frightened | general d20 disadvantage pressure |
| Grappled | blocks movement, attack disadvantage |
| Incapacitated | cannot act |
| Invisible | grants attack advantage until broken by hostile action |
| Paralyzed | cannot act, auto-fails STR/DEX saves |
| Petrified | cannot act, auto-fails STR/DEX saves, halves incoming damage |
| Poisoned | general d20 disadvantage pressure |
| Burning | takes `1d6` fire at end of turn |
| Acid-Burned | takes `1d4` acid at end of turn, `-1 AC` |
| Reeling | `-2 attack` |
| Prone | `-2 AC`, melee attackers gain advantage, ranged attackers take disadvantage |
| Restrained | `-2 AC`, attack disadvantage, blocks movement, DEX save disadvantage |
| Emboldened | `+2 attack`, `+1 saves` |
| Blessed | `+1 attack`, `+2 saves` |
| Guarded | `+1 AC` |
| Marked | enemy focus-fire hook; attacks against the target gain extra pressure in some archetypes |
| Bleeding | takes `1d4` bleeding damage at end of turn |
| Cursed | `-1 attack`, `-1 saves`, not marked combat-only |
| Resist Fire / Cold / Lightning / Poison | grants matching damage resistance |
| Stunned | cannot act |
| Unconscious | represented when current HP is 0 and not dead |

## Enemy-Independent Damage And Survival Rules

- Resistances halve incoming matching damage
- Temporary HP absorbs damage before current HP
- Effective armor class now accounts for both AC penalties and AC bonuses such as `Guarded`
- Fire resistance can come from Fire-Blooded ancestry or item/status resistance
- Poison resistance can come from Dwarf ancestry or item/status resistance
- Dropping a hero to 0 HP starts death-save state
- Hitting a hero already at 0 HP causes a death-save failure instead of normal HP loss
- Enemies die immediately at 0 HP
- After combat, living heroes at 0 HP recover to 1 HP automatically

### Death saves

- DC `10`
- Natural `1`: two failures
- Natural `20`: stand up at `1` HP
- `3` successes: stabilize at `0`
- `3` failures: die

## Items, Resting, And Inventory

### Shared inventory

- Inventory is party-shared
- Carrying capacity is computed from the party
- Weight and supply points are tracked
- Equipment can be assigned to any company member

### Resting

- Short rests per long rest: `2`
- Short rest:
  - heals each living party member for half maximum HP, rounded up
  - restores short-rest resources like Second Wind, Action Surge, Channel Divinity, and ki
  - restores half maximum MP, rounded up, for Mage MP users
  - restores all MP for Warlocks
  - Arcane Recovery and Natural Recovery still restore one hidden compatibility spell slot while combat casting uses MP
- Long rest:
  - costs `12` supply points
  - fully restores HP, MP, and other resources for living members
  - resets short rests to `2`
  - clears temporary combat conditions
  - reduces Exhaustion by `1`

### Consumable timing

- Drinking a healing potion yourself in combat is a bonus action
- Using an item on someone else in combat is an action
- Scroll of Revivify works at camp on dead companions only
- The current item implementation supports healing, temp HP, revive HP, MP restoration through former spell-slot-refresh items, poison cure, condition clearing, and condition application

### Item catalog

- The full generated item reference already lives in `information/catalogs/ITEM_CATALOG.md`
- Use that file for concrete weights, rarities, acquisition sources, weapon properties, armor entries, consumables, and scroll effects

## Notes For Debugging

- Many race and class feature tags are descriptive identifiers, while only a subset have hard-coded effects
- Enemy behavior is driven more by `archetype` checks than by generic feature tags
- Companion relationship bonuses stack into the same bonus channels used by gear and level progression
- A few Act 1 story systems now sit in `map_system.py` rather than classic linear scene files, including hidden-route unlocks, companion personal quests, and the ending-tier calculation
- Character creation stores a few legacy display names like `Healing Potion`, but active gameplay inventory uses normalized item ids like `potion_healing`
