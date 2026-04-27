# Aethrune Companion Class Retcon Mapping

This draft maps the companion roster onto the new Warrior, Rogue, and Mage structure.

Runtime ids should stay stable during the first implementation pass. Public text can use the retcon names from the companion ideology matrix while save keys keep their current values.

Companion subclass choice opens at level 3 for anyone recruited at level 1 or 2. A companion already level 3 or higher when recruited receives the listed primary focus automatically.

Runtime subclass focus now prunes companion feature grants. Player-built versions of Warrior, Rogue, and Mage still use the broad testing packages until the player subclass pass happens.

## Roster Map

| Companion | Runtime id | Current class | Retcon class | Primary focus | Secondary focus | Party job |
| --- | --- | --- | --- | --- | --- | --- |
| Tolan Ironshield | `tolan_ironshield` | Fighter | Warrior | Juggernaut | Weapon Master | shield wall, Guard tank, Fixated control |
| Bryn Underbough | `bryn_underbough` | Rogue | Rogue | Shadowguard | Assassin | avoidance tank, decoys, exposed targets |
| Elira Lanternward | `elira_dawnmantle` | Cleric | Mage | Aethermancer | Spellguard | healer, Ward overflow, condition repair |
| Kaelis Starling | `kaelis_starling` | Ranger | Rogue | Assassin | Shadowguard | ranged opener, Death Mark, scout pressure |
| Rhogar Valeguard | `rhogar_valeguard` | Paladin | Warrior | Bloodreaver | Juggernaut | oath mark, ally sustain, armored pressure |
| Nim Ardentglass | `nim_ardentglass` | Wizard | Mage | Arcanist | Spellguard | Pattern Read, Arc setup, force damage |
| Irielle Ashwake | `irielle_ashwake` | Warlock | Mage | Elementalist | Arcanist | signal disruption, elemental pressure, save attacks |

## Companion Details

### Tolan Ironshield

Tolan becomes the cleanest Warrior conversion. His shield has a notched tower-rivet from Blackwake, and every combat habit points toward Guard, Brace, raised shield, and holding a bad angle until the party can breathe.

Mechanical target:
- `class_name`: `Warrior`
- keep dwarf, Soldier, shield, heavy armor, longsword
- keep STR and CON high; keep CHA usable for command voice
- preferred stance: Guard
- preferred resources: Grit and Momentum
- preferred actions: Take Guard Stance, Raise Shield, Iron Draw, Shoulder In, Pin
- relationship bonuses should move from legacy `AC` toward `defense_percent`, `stability`, or `CON_save`

Combat identity:
Tolan should make enemies spend turns into the wrong place. He Fixates dangerous melee enemies, stacks Defense through Guard, and uses Shoulder In when the party needs room.

Implementation test:
- build Tolan, level to 4, verify `class_name == "Warrior"`
- verify `grit`, `momentum`, Guard actions, Iron Draw, and Shoulder In appear
- verify Guard plus shield produces the expected Defense and Stability

### Bryn Underbough

Bryn already sits on the Rogue chassis. Her retcon focus should lean into Shadowguard because her best scenes are exits, blind spots, decoys, bad floorboards, and the half-second before a room turns violent.

Mechanical target:
- `class_name`: `Rogue`
- keep halfling, Criminal, finesse weapon
- keep expertise in Stealth and Perception
- preferred resources: Edge and Shadow
- preferred actions: Tool Read, Skirmish, False Target, Smoke Pin, Cover The Healer
- secondary actions: Death Mark and Quiet Knife when the party has another defender

Combat identity:
Bryn protects the party by making the enemy read the room wrong. She can cover Elira, bait misses, and create exposed targets for the player.

Implementation test:
- build Bryn, level to 4, verify Shadowguard actions appear
- verify False Target and Smoke Pin interact with Edge and Shadow
- verify her opener still grants a stealth or ambush advantage without breaking Rogue resource setup

### Elira Lanternward

Elira should move from Cleric to Mage with an Aethermancer focus. Her Lantern work becomes field medicine, breath control, triage marks, and Ward overflow. She keeps the language of mercy because her mechanics now make mercy practical under pressure.

Mechanical target:
- runtime id remains `elira_dawnmantle`
- public text should use Elira Lanternward where the retcon pass touches prose
- `class_name`: `Mage`
- `spellcasting_ability`: `WIS`
- preferred resources: MP, Flow, Ward
- preferred actions: Field Mend, Pulse Restore, Clean Breath, Triage Line, Overflow Shell, Anchor Shell
- relationship bonuses should prefer `healing`, `WIS_save`, and possibly `ward`

Combat identity:
Elira keeps people upright. She heals low allies to build Flow, turns excess healing into Ward, and clears Poisoned, Bleeding, or Reeling before those statuses spiral.

Implementation test:
- build Elira, level to 4, verify `class_name == "Mage"` and `spellcasting_ability == "WIS"`
- verify Flow cap 5, Field Mend, Pulse Restore, Clean Breath, Triage Line, and Overflow Shell
- verify her healing math uses Wisdom after the conversion
- verify Lantern Ward opener maps cleanly to Ward, blessed, or guarded support

### Kaelis Starling

Kaelis should become a Rogue with Assassin focus. His ranger identity is still present through bow work, trail read, target selection, and first-angle discipline. The class conversion gives him Death Mark and exposed-target play without needing the old Ranger chassis.

Mechanical target:
- `class_name`: `Rogue`
- keep bow or finesse backup weapon; primary combat weapon should be a longbow or shortbow
- keep Perception, Stealth, Survival
- preferred resources: Edge, Death Mark
- preferred actions: Tool Read, Death Mark, Quiet Knife, Between Plates, Skirmish
- secondary Shadowguard tools can represent smoke-line movement and overwatch

Combat identity:
Kaelis names the target that will break the line first. He should open fights by marking scouts, archers, or casters, then keep ranged pressure on exposed targets.

Implementation test:
- build Kaelis, level to 4, verify `class_name == "Rogue"`
- verify ranged Rogue attacks still calculate Sneak Attack correctly
- verify Death Mark and Assassin accuracy work with his bow
- verify his scene support still grants ambush or attack-pressure effects

### Rhogar Valeguard

Rhogar should become a Warrior with Bloodreaver focus. His oath turns into a visible debt system: he marks a foe, takes the cost seriously, and pushes stolen momentum back into allies. The blood language should read as oath-price and battlefield sacrifice, not cruelty.

Mechanical target:
- `class_name`: `Warrior`
- keep dragonborn, Soldier, shield, heavy armor, longsword
- preferred resources: Grit and Blood Debt
- preferred actions: Red Mark, Blood Price, War-Salve Strike, Open The Ledger, Guard
- secondary Juggernaut tools support his oath-guardian role
- relationship bonuses should prefer `damage`, `defense_percent`, or `WIS_save`

Combat identity:
Rhogar names a threat and makes the party safer by forcing that threat to matter. He uses Blood Price as oath-medicine and War-Salve Strike when a wounded ally needs a narrow recovery window.

Implementation test:
- build Rhogar, level to 4, verify `class_name == "Warrior"`
- verify Blood Debt cap, Red Mark, Blood Price, War-Salve Strike, and Open The Ledger
- verify Blood Price heals an ally and applies the intended Reeling cost
- verify Oath Challenge opener maps to marked, emboldened, or guarded pressure

### Nim Ardentglass

Nim should become a Mage with Arcanist focus. He reads structures as arguments, so Pattern Read and Pattern Charge fit his route marks, old mechanisms, and careful fear. His Spellguard secondary covers caution around unstable ruins.

Mechanical target:
- `class_name`: `Mage`
- `spellcasting_ability`: `INT`
- preferred resources: MP, Focus, Arc
- preferred actions: Pattern Read, Marked Angle, Arc Pulse, Detonate Pattern, Anchor Shell
- relationship bonuses should prefer `Arcana`, `Investigation`, `spell_attack`, and `spell_damage`

Combat identity:
Nim turns a fight into a diagram. He reads the weakest resist lane, builds Pattern Charge, and detonates only when the line is clean.

Implementation test:
- build Nim, level to 4, verify `class_name == "Mage"`
- verify Pattern Read, Arc Pulse, Marked Angle, Detonate Pattern, Arc cap, and Focus
- verify Pattern Read calls out Defense, Avoidance, Ward, and weakest save
- verify Surveyor's Angles opener maps to attack pressure or Pattern Read setup

### Irielle Ashwake

Irielle should become a Mage with Elementalist focus. Her Fire-Blooded identity and Quiet Choir escape both point toward unstable signal, counter-cadence, fire, lightning, and channel pressure. Arcanist secondary lets her understand the Choir pattern without letting it own her.

Mechanical target:
- `class_name`: `Mage`
- `spellcasting_ability`: `CHA`
- preferred resources: MP, Focus, Attunement
- preferred actions: Ember Lance, Volt Grasp, Change Weather, Burning Line, Lockfrost
- secondary actions: Pattern Read and Arc Pulse for Choir-pattern scenes
- relationship bonuses should prefer `spell_damage`, `Insight`, and `WIS_save`

Combat identity:
Irielle breaks enemy rhythm. She swaps elements to trigger weave riders, pressures saves, and uses lightning or fire when a signal needs to be interrupted quickly.

Implementation test:
- build Irielle, level to 4, verify `class_name == "Mage"` and `spellcasting_ability == "CHA"`
- verify Attunement cap, Ember Lance, Volt Grasp, Burning Line, Lockfrost, and Change Weather
- verify Elemental Weave can apply a rider after changing elements
- verify Counter-Cadence opener maps to blessed, attack pressure, or enemy save pressure

## Party Shape After Conversion

The converted roster gives:
- two Warriors: Tolan and Rhogar
- two Rogues: Bryn and Kaelis
- three Mages: Elira, Nim, and Irielle

That spread gives the player a full combat triangle from companions alone:
- armored line: Tolan or Rhogar
- avoidance and target work: Bryn or Kaelis
- channel support: Elira, Nim, or Irielle

The active party limit means duplicate class roles create choice instead of clutter. Tolan and Rhogar should feel different because Tolan denies space while Rhogar pays costs into allies. Nim and Irielle should feel different because Nim solves a pattern while Irielle disrupts a signal. Bryn and Kaelis should feel different because Bryn protects through misdirection while Kaelis deletes a priority target.

## Implementation Order

1. Bryn Underbough

Bryn already uses Rogue. Start here to prove companion leveling still exposes the new Rogue tools.

2. Tolan Ironshield

Convert Fighter to Warrior and test Guard, shield Defense, Grit, Momentum, and companion opener support.

3. Elira Lanternward

Convert Cleric to Mage/Aethermancer because she carries the party's healer expectation. Verify Wisdom-based healing before touching the other Mage companions.

4. Nim Ardentglass

Convert Wizard to Mage/Arcanist. He tests Pattern Read and save-lane logic from a real companion.

5. Kaelis Starling

Convert Ranger to Rogue/Assassin after Bryn is stable. His ranged Rogue setup needs specific Sneak Attack and Death Mark tests.

6. Rhogar Valeguard

Convert Paladin to Warrior/Bloodreaver. He has the most thematic translation work because oath healing, mark pressure, and Blood Debt need careful public wording.

7. Irielle Ashwake

Convert Warlock to Mage/Elementalist. She should come after Nim so the Mage conversion path is already tested, then she can focus on Attunement and elemental rider behavior.

## Code Touchpoints

Expected files:
- `dnd_game/data/story/factories.py`
- `dnd_game/data/story/companions.py`
- `dnd_game/data/story/public_terms.py`
- `dnd_game/gameplay/combat_flow.py`
- `dnd_game/gameplay/combat_simulator.py`
- `tests/test_core.py`
- `tests/test_combat_resolver.py`
- new companion conversion tests if the existing suites get too dense

Useful implementation helper:
- add a small companion retcon helper that applies class overrides after `build_character`
- keep old companion ids and recruitment flags stable
- set companion-specific `spellcasting_ability` overrides after construction where needed
- set weapons after construction for Kaelis and Bryn so Rogue identity can support ranged or finesse play

## Required Tests

Minimum test matrix:
- every companion can be built
- every companion can be leveled to 4
- converted class name matches this mapping
- expected resource caps exist after combat prep
- expected combat options appear
- relationship bonuses still apply
- combat opener still applies valid statuses
- full encounter pass can use at least one real companion in each role

Companion-specific assertions:
- Tolan: Guard Defense and Stability increase
- Bryn: False Target and Smoke Pin consume and grant the right resources
- Elira: Field Mend uses Wisdom and overflow creates Ward
- Kaelis: bow attacks can trigger Rogue damage and Death Mark pressure
- Rhogar: Blood Price heals and applies its cost
- Nim: Pattern Read plus Marked Angle builds Arc and Pattern Charge
- Irielle: Change Weather plus Elementalist channel applies Attunement and weave riders
