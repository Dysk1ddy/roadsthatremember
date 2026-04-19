# Inn Expansion Draft

This draft expands inn content into a repeatable social gameplay layer instead of a single rumor-and-rest stop.

It is written to fit the current Act 1 and early Act 2 structure, especially:

- `scene_neverwinter_briefing()` in `dnd_game/gameplay/story_intro.py`
- `visit_stonehill_inn()` in `dnd_game/gameplay/story_town_hub.py`
- the current quest system documented in `information/systems/QUEST_SYSTEM_REFERENCE.md`
- the current NPC and companion roster documented in `information/catalogs/NPCS.md`

## Design Goals

- Make inns feel like dense social hubs instead of one-screen utility stops.
- Add more named non-companion NPCs who can recur across chapters.
- Create optional low-stakes and mid-stakes social content between combat nodes.
- Give the player more opportunities for `Persuasion`, `Insight`, `Deception`, `Intimidation`, `Performance`, `Sleight of Hand`, `Medicine`, and `Backtrack`.
- Seed side quests that encourage returning to town instead of only moving forward.
- Add tavern trouble scenes, especially bar fights, cheating accusations, loud arguments, and Ashen Brand intimidation attempts.
- Make party identity matter in town through class, race, and story-modifier checks.

## Recommended Structure

Each inn should support four layers of interaction:

1. `Room tone`
   - short rotating arrival text
   - crowd mood shifts based on story flags
2. `Named NPC loop`
   - 3-5 named interactable NPCs
   - each with at least two talk beats and one unlock beat
3. `Inn actions`
   - buy a round
   - eavesdrop
   - gamble
   - private-room meeting
   - settle a dispute
   - rent beds
4. `Pressure event`
   - bar fight
   - sabotage
   - intimidation visit
   - theft accusation

## Shared Inn Actions

These can be reused in most inns with different flavor text.

### Buy A Round

- Cost: `2-6 gp` depending on inn size and chapter
- Effect:
  - raises one local rumor reveal
  - can improve disposition with one inn NPC
  - may reveal a hidden quest giver

Suggested checks:

- `Persuasion`: turn a paid drink into useful conversation
- `Insight`: spot who is staying quiet on purpose
- `Deception`: pretend to be less informed than you are

### Eavesdrop

- Free
- Can reveal one clue, one false lead, or one faction tell

Suggested checks:

- `Perception`: catch a name, route, or time
- `Insight`: identify the liar at the table
- `Stealth`: listen without becoming the room's business

### Cards / Dice / Knife Toss

- Small gold stakes
- A good place for social failure without full story failure

Suggested checks:

- `Sleight of Hand`: cheat cleanly
- `Insight`: catch someone else's cheat
- `Performance`: play to the room while gambling
- `Intimidation`: collect a debt after a caught cheat

### Ask For Private Room

- Good for quest turn-ins, blackmail, contraband offers, and companion scenes
- Can gate sensitive content behind:
  - `Persuasion`
  - faction flags
  - quest readiness
  - `Liar's Blessing`

### Step Into The Trouble

- Used when an argument is escalating
- Lets the player prevent, redirect, or start a bar fight

Suggested checks:

- `Persuasion`: calm the room
- `Intimidation`: make both sides stand down
- `Insight`: name the real problem and embarrass the aggressor
- `Athletics`: physically separate the brawlers
- `Deception`: fabricate a threat, guard call, or witness

## Neverwinter Inn Expansion

The current Neverwinter inn interaction is only a rest option during the briefing. This draft treats it as Mira's contract house: a discreet tavern where road-hands, teamsters, scouts, and off-duty civic agents cross paths.

Suggested location tone:

```text
The contract house near the river keeps its candles low and its doors watched. Teamsters drink beside scribes who are pretending not to be scribes, and every quiet table feels rented by someone who expects trouble before dawn.
```

### New Neverwinter NPCs

#### 1. Oren Vale, contract host

- Role: inn steward and fixer of small private arrangements
- Tone: polite, dry, impossible to surprise
- Use:
  - introduces private-room scenes
  - quietly remembers whether the player pays debts, starts fights, or protects staff
  - can unlock a later Neverwinter favor flag

Sample dialogue:

```text
"I don't mind dangerous people. I mind loud ones. Dangerous and quiet can still finish a meal."
```

```text
"If Mira sent you, then you're here for one of three things: a contract, a witness, or a bed you won't really sleep in."
```

Suggested flags:

- `neverwinter_oren_met`
- `neverwinter_oren_trust`
- `quest_reward_oren_private_room_access`

#### 2. Sabra Kestrel, caravan bookkeeper

- Role: nervous logistics clerk tracking missing wagons
- Tone: sharp memory, frayed nerves
- Use:
  - can grant an early inn quest about forged manifests
  - good source of route names and timetables
  - ties city-side sabotage to later Phandalin supply pressure

Sample dialogue:

```text
"Missing cargo would bother me less if it stayed missing honestly. These ledgers are being corrected by someone who expects not to be checked."
```

Suggested check gates:

- `Investigation`: read the altered ledger entries
- `Persuasion`: convince Sabra to let you see restricted notes
- `Insight`: notice which missing caravan frightens her most

Suggested quest:

- `false_manifest_circuit`
- Objective: identify which road inspection papers are forged before departure
- Reward ideas:
  - `25-40 gp`
  - `40-60 XP`
  - clue flag for Blackwake or High Road branches
  - discount or leverage with Oren

#### 3. Vessa Marr, dockside card sharp

- Role: charming cheat, rumor broker, possible light criminal contact
- Tone: flirtatious, dangerous in small ways
- Use:
  - gambling scene
  - can point toward Blackwake, false seals, or smuggling routes
  - possible future callback if Bryn is present

Sample dialogue:

```text
"Everyone lies at cards. The interesting thing is what they choose not to lie about."
```

```text
"You can tell a city is getting afraid when even the cheaters start buying good boots."
```

Suggested checks:

- `Sleight of Hand`: cheat her
- `Insight`: catch her cheat
- `Deception`: bluff a fake road identity
- `Persuasion`: turn flirtation into actual help

Possible outcome:

- no quest, but grants one of:
  - `blackwake_millers_ford_lead`
  - `road_patrol_writ`
  - `neverwinter_smuggler_phrase_known`

#### 4. Garren Flint, off-duty roadwarden

- Role: bitter veteran who suspects corruption but fears naming names
- Tone: proud, guarded, half-ashamed
- Use:
  - strong `Insight` or `Intimidation` scene
  - can reveal how forged authority is getting traction
  - can also become the spark for a bar fight if pushed badly

Sample dialogue:

```text
"A fake seal only works if honest people are already tired enough to obey it."
```

```text
"Don't ask me which officers are clean in a crowded room. Ask me which ones are suddenly prosperous."
```

Suggested checks:

- `Insight`: realize he is protecting a frightened subordinate
- `Intimidation`: force a partial name
- `Persuasion`: get him to share route signs and habits

### Neverwinter Inn Options

- `Buy a round for the teamsters`
- `Ask Oren for a private room`
- `Play cards with Vessa Marr`
- `Press Garren Flint on false roadwarden seals`
- `Review ledgers with Sabra Kestrel`
- `Try to recruit one extra road contact before departure`
- `Rent beds for a long rest`

### Neverwinter Bar Fight Event: Ash In The Ale

Trigger ideas:

- first or second visit only
- player wins too much money from Vessa
- player pushes Garren too hard
- `blackwake_started` is false and the room still feels pre-departure

Setup:

```text
A cup strikes the wall hard enough to silence three nearby tables. One teamster is on his feet, red-faced and shaking, while another man swears the ale was dosed and the game rigged. Nobody draws steel yet, but the room has started choosing sides.
```

Player choices:

1. `PERSUASION`: "Sit down and talk before someone earns a broken jaw."
2. `INSIGHT`: identify the actual liar
3. `SLEIGHT OF HAND`: quietly swap the marked die / loaded cup
4. `INTIMIDATION`: make the loudest fool back down
5. `ATHLETICS`: step between them when furniture starts moving
6. `Do nothing`

Outcomes:

- success:
  - gain room trust
  - unlock extra rumor or quest lead
  - possible `+1` Oren trust
- failure:
  - tavern brawl combat using improvised weapons
  - small gold loss or bruised condition
  - later staff suspicion

Possible reward hook:

- `quest_reward_contract_house_favor`

## Stonehill Inn Expansion

Stonehill is already the main town social hub and should become the game's richest recurring inn.

Suggested tone:

```text
The Stonehill common room is where fear goes when it wants company. Miners lean over watered ale, drovers rehearse bad news before taking it home, and anyone who speaks too confidently gets watched like they may be selling a miracle.
```

### New Stonehill NPCs

#### 1. Mara Stonehill, acting floorkeeper

- Role: keeps order, remembers faces, quietly triages who is too drunk, too dangerous, or too desperate
- Tone: practical warmth with a blade under it
- Use:
  - opens or closes inn trouble scenes
  - can thank the player for defending the room
  - can become a repeatable source of "what the room feels like tonight"

Sample dialogue:

```text
"If you're here to save the town, good. If you're here to practice on it, finish your drink outside."
```

#### 2. Jerek Harl, miner with a grievance

- Role: angry local whose brother vanished on the road
- Tone: exhausted, suspicious, easy to ignite
- Use:
  - turns road fear into a personal quest
  - can fight the player, admire the player, or later thank the player

Sample dialogue:

```text
"People keep saying 'raids' like that's better than murder. My brother had a name before he became a warning."
```

Suggested quest:

- `find_harls_brother`
- Objective: confirm the fate of Dain Harl from signs near Ashfall Watch or a roadside branch
- Reward ideas:
  - gold from pooled family savings
  - a keepsake charm
  - town-fear reduction

#### 3. Sella Quill, traveling singer and rumor collector

- Role: performer who hears everything because everyone wants to impress her
- Tone: bright, curious, smarter than she looks
- Use:
  - Performance scene
  - social shortcut NPC for multiple route rumors
  - can unlock a better crowd outcome if the player has `Liar's Blessing`

Sample dialogue:

```text
"People tell the truth in songs by accident. That's why I stay through the second chorus."
```

Suggested checks:

- `Performance`: trade a song, story, or boast
- `Persuasion`: ask who in the room is worth hearing
- `Insight`: catch which rumor she does not believe

#### 4. Old Tam Veller, retired prospector

- Role: half-dismissed old-timer with real memory for ruins, wells, and side paths
- Tone: rambling until he is not
- Use:
  - can hint `Old Owl Well`, hidden cellar routes, old survey shafts, or wilderness branches
  - great for `Insight` and patience-based scene writing

Sample dialogue:

```text
"Young people think a ruin starts where the roof is missing. A ruin starts where people stopped agreeing on what it was for."
```

#### 5. Nera Doss, courier with a split lip

- Role: recurring messenger, secretly skimming information for a local pressure group or later faction
- Tone: competent, hurt, unwilling to look weak
- Use:
  - `Medicine` or `Persuasion` scene
  - can pay off into a courier-network flag
  - may be the victim in an inn intimidation event

Sample dialogue:

```text
"I fell, that's all. And if you believe that, you haven't spent much time around men who want messages to arrive edited."
```

### Stonehill Inn Options

- `Buy a round and listen for fresh road talk`
- `Sit with Bryn Underbough`
- `Check whether Tolan is still resting here`
- `Listen to Sella Quill perform`
- `Talk to Jerek Harl about the missing road crews`
- `Hear Old Tam Veller out`
- `Treat Nera Doss's injuries`
- `Play cards or bones for small coin`
- `Break up a dispute before it turns into a fight`
- `Ask for a private room to discuss ready quests or quiet business`
- `Rent beds for a long rest`

## Stonehill Quest And Trouble Drafts

### Quest: Last Shift On The East Road

- Giver: Jerek Harl
- Type: grief-driven local quest
- Unlock: first or second Stonehill visit
- Objective:
  - find proof of what happened to his brother's crew
  - proof can be remains, a signet, a written note, or a surviving witness
- Turn-in:
  - Jerek at Stonehill Inn
- Rewards:
  - meaningful XP and gold
  - `harl_family_charm`
  - `act1_town_fear -1`
  - inn crowd reaction line on completion

Turn-in tone:

```text
Jerek does not thank you quickly. First he reads the proof twice. Then he sits down because standing has become harder than grief for a moment.
```

### Quest: The Marked Keg

- Giver: Mara Stonehill or Oren Vale
- Type: inn sabotage / poison / smuggling investigation
- Objective:
  - inspect keg marks
  - follow who paid for the tampered cask
  - decide whether it was extortion, theft, or a warning
- Checks:
  - `Investigation`
  - `Insight`
  - `Deception`
  - `Sleight of Hand`
- Good fit for a no-combat or light-combat branch

Reward ideas:

- `innkeeper_credit_token`
- `20-50 gp`
- room discount flag
- extra local support during later town pressure scenes

### Quest: Songs For The Missing

- Giver: Sella Quill
- Type: social / memorial quest
- Objective:
  - gather three true details about the dead or missing
  - return so Sella can turn rumor into remembrance
- Tone:
  - quieter than the other inn content
  - good contrast with brawls and swagger
- Rewards:
  - XP
  - `sella_ballad_token`
  - town morale / fear benefit

### Quest: Quiet Table, Sharp Knives

- Giver: hidden; emerges through eavesdropping
- Type: secret meeting / ambush prevention
- Objective:
  - overhear an Ashen Brand-linked exchange in a private room
  - choose whether to expose it, extort it, or follow it
- Checks:
  - `Stealth`
  - `Perception`
  - `Deception`
  - `Backtrack`

Possible unlocks:

- alternate approach to a road branch
- future blackmail flag
- merchant leverage

## Stonehill Bar Fight Draft: Miners, Mercenaries, And Bad Timing

This should be a signature inn event, not just a random tavern brawl.

Trigger ideas:

- after one major side quest is cleared
- before Ashfall Watch, when town fear is still high
- when Jerek Harl has been drinking and rumors of missing crews sharpen
- when a loud mercenary or disguised Ashen Brand plant mocks the town

Setup:

```text
The room has been running hot all evening, but the break comes fast. A hired blade from out of town laughs at the miners for hiding behind doors, Jerek Harl hears only the insult and not the ale behind it, and a bench goes over before anyone finishes choosing whose side they are on.
```

Player choices:

1. `PERSUASION`: pull the insult back from the edge
2. `INSIGHT`: call out the disguised instigator
3. `INTIMIDATION`: shut the room down with sheer force
4. `ATHLETICS`: grab the first chair before it flies
5. `PERFORMANCE`: turn the room with a loud toast, joke, or challenge
6. `Join the fight`

Success outcomes:

- reduce `act1_town_fear`
- improve Stonehill goodwill
- unlock a hidden witness
- Bryn or Tolan approval depending on approach

Failure outcomes:

- improvised-weapon encounter
- one NPC injured or offended
- inn gets tense for the next visit
- possible resting surcharge or no-private-room consequence

Hidden twist:

- on `Insight` success, the instigator is an Ashen Brand paid mouth trying to keep Phandalin angry, divided, and easy to predict

## Special Checks And Story Modifier Hooks

### Liar's Blessing

This modifier should matter in inns more than almost anywhere else.

Suggested uses:

- unique bluff options in card games
- cleaner lie to protect a frightened witness
- special social line against a cheater or plant
- automatic or reduced-DC success on one rumor extraction per inn

Example tagged option:

```text
[LIAR'S BLESSING] Smile like you already know who rigged the game, and wait for the guilty one to correct you.
```

### Liar's Curse

Suggested uses:

- increase the chance the room reads the player as shifty
- make bluff attempts riskier
- add a line where an NPC says the player's face looks "half a step behind their own lie"

### Backtrack

Inns are ideal places to spend `Backtrack`.

Suggested uses:

- revisit a rumor after a road discovery
- turn in proof to the original speaker instead of only formal quest givers
- unlock "I heard you mention this earlier" dialogue that rewards paying attention

## Companion Reactions

Inns should be one of the best places to surface companion personality.

Suggested pairings:

- Bryn:
  - bonuses on rumor, cheating, and liar-detection scenes
  - approval if the player reads the room well
- Tolan:
  - bonuses on breaking up fights honorably
  - approval if the player protects civilians without swagger
- Elira:
  - bonuses when treating injured NPCs or calming grief
  - disapproval if the player starts violence for sport
- Kaelis:
  - bonuses on eavesdropping and spotting the watcher who does not belong
- Rhogar:
  - bonuses on public vows, order, and intimidation used to prevent harm

## Suggested Implementation Hooks

This is still a draft, but these hooks would fit the current codebase cleanly.

### Flags

Examples:

- `stonehill_barfight_seen`
- `stonehill_barfight_won_socially`
- `stonehill_barfight_brawled`
- `stonehill_npc_jerek_met`
- `stonehill_npc_sella_met`
- `stonehill_private_room_unlocked`
- `neverwinter_contract_house_seen`
- `neverwinter_vessa_cards_played`
- `neverwinter_oren_trust`
- `inn_marked_keg_started`
- `inn_marked_keg_resolved`

### Quest ids

Possible additions:

- `false_manifest_circuit`
- `find_harls_brother`
- `marked_keg_investigation`
- `songs_for_the_missing`
- `quiet_table_sharp_knives`

### Reward items

If quest rewards need unique items, these fit well in the catalog:

- `harl_family_charm`
- `innkeeper_credit_token`
- `sella_ballad_token`
- `loaded_bone_dice`
- `roadwarden_tabard_patch`
- `blackseal_taster_pin`

## Best First Wave

If only a few inn additions are implemented first, these are the highest-value set:

1. Expand Stonehill with two new named NPCs: Jerek Harl and Sella Quill.
2. Add one Stonehill bar fight with three to six resolutions.
3. Add one Stonehill grief quest that must be turned in at the inn.
4. Add one Neverwinter card-sharp NPC and one private-room rumor scene.
5. Add `Liar's Blessing`-specific inn dialogue options.

That set would make inns feel alive immediately without requiring a full tavern simulation layer.
