# Aethrune ID Migration Plan

Last updated: 2026-04-27

This plan moves save-sensitive legacy IDs toward Aethrune names without breaking old saves. The runtime should keep a central alias layer in place before broad renames begin, because a single old scene key can appear in save JSON, map state, quest logs, tests, music tables, journal summaries, and console commands.

## Migration Rules

- Keep old IDs readable through the alias layer until at least one stable release after the rename pass.
- Add aliases before renaming call sites.
- Normalize loaded saves through runtime IDs while the old handler names still own the scene code.
- Write canonical IDs only after the matching scene, map, quest, and flag references have moved together.
- Keep public labels Aethrune-facing throughout the transition.

## Scene IDs

| Legacy ID | Target ID | Public label | Runtime status | Risk | Notes |
| --- | --- | --- | --- | --- | --- |
| `neverwinter_briefing` | `greywake_briefing` | Greywake Briefing | active | high | Dispatch, music, Act 1 map node, tests, saves. |
| `phandalin_hub` | `iron_hollow_hub` | Iron Hollow | active | high | Hub routing, quest turn-ins, map state, save previews. |
| `high_road_liars_circle` | `emberway_liars_circle` | Liar's Circle | active | medium | Side branch scene, tests, companion support. |
| `high_road_false_checkpoint` | `emberway_false_checkpoint` | False Checkpoint | active | medium | Side branch scene and route flags. |
| `high_road_false_tollstones` | `emberway_false_tollstones` | False Tollstones | active | medium | Side branch scene and route flags. |
| `old_owl_well` | `blackglass_well` | Blackglass Well | active | high | Dungeon map, quest, room flags, companion support. |
| `wyvern_tor` | `red_mesa_hold` | Red Mesa Hold | active | high | Dungeon map, quest, route unlocks. |
| `tresendar_manor` | `duskmere_manor` | Duskmere Manor | active | high | Act 1 late dungeon, boss route, Act 1 completion path. |
| `wave_echo_outer_galleries` | `resonant_vault_outer_galleries` | Resonant Vault Outer Galleries | active | high | Act 2 late route and smoke tests. |
| `black_lake_causeway` | `blackglass_causeway` | Blackglass Causeway | active | medium | Act 2 route state and Forge handoff flags. |
| `forge_of_spells` | `meridian_forge` | Meridian Forge | active | high | Act 2 finale, Act 3 handoff, boss route. |
| `neverwinter_wood_survey_camp` | `greywake_survey_camp` | Greywake Survey Camp | active | medium | Act 2 early lead and survey route flags. |
| `conyberry_agatha` | `hushfen_pale_circuit` | Hushfen and the Pale Circuit | alias active | low | Already normalized by save integrity checks. |

## Quest IDs

| Legacy ID | Target ID | Public label | Runtime status | Risk | Notes |
| --- | --- | --- | --- | --- | --- |
| `restore_barthen_supplies` | `restore_hadrik_supplies` | Hadrik's missing supplies | active | medium | Old quest saves canonicalize through the quest log. |
| `break_wyvern_tor_raiders` | `break_red_mesa_raiders` | Red Mesa raiders | active | medium | Tied to route unlocks and Red Mesa completion. |
| `seek_agathas_truth` | `seek_pale_witness_truth` | Pale Witness truth | alias active | low | Already canonicalized in quest log handling. |

## Flag IDs

| Legacy ID | Target ID | Runtime status | Notes |
| --- | --- | --- | --- |
| `phandelver_claims_council_seen` | `iron_hollow_claims_council_seen` | alias active | Act 2 council memory. |
| `phandalin_sabotage_resolved` | `iron_hollow_sabotage_resolved` | alias active | Act 2 midpoint result. |
| `act3_phandalin_state` | `act3_iron_hollow_state` | alias active | Act 3 inheritance. |
| `briefing_q_neverwinter` | `briefing_q_greywake` | active | Mira's Greywake briefing question. |
| `briefing_q_phandalin` | `briefing_q_iron_hollow` | active | Mira's Iron Hollow briefing question. |
| `old_owl_*` | `blackglass_well_*` | active | Blackglass Well room, route, and boss flags. |
| `wyvern_*` | `red_mesa_*` | active | Red Mesa room, route, and boss flags. |
| `tresendar_*` | `duskmere_*` | active | Duskmere room, route, and boss flags. |
| `agatha_*` | `pale_witness_*` / `pale_circuit_*` | alias active | Hushfen/Pale Witness route. |
| `conyberry_*` | `hushfen_*` | alias active | Hushfen route and Blackglass/Forge payoffs. |
| `black_lake_conyberry_*` | `blackglass_hushfen_*` | alias active | Blackglass causeway payoff flags. |
| `forge_conyberry_*` | `forge_hushfen_*` | alias active | Meridian Forge payoff flags. |

## Map Node And Dungeon IDs

| Legacy ID | Target ID | Runtime status | Notes |
| --- | --- | --- | --- |
| `phandalin_hub` | `iron_hollow_hub` | active | Act 1 map node and hub scene. |
| `old_owl_well` | `blackglass_well` | active | Act 1 node and dungeon. |
| `wyvern_tor` | `red_mesa_hold` | active | Act 1 node and dungeon. |
| `tresendar_manor` | `duskmere_manor` | active | Act 1 node and dungeon. |
| `phandalin_claims_council` | `iron_hollow_claims_council` | active | Act 2 map start node. |
| `neverwinter_wood_survey_camp` | `greywake_survey_camp` | active | Act 2 early route. |
| `wave_echo_outer_galleries` | `resonant_vault_outer_galleries` | active | Act 2 late dungeon. |
| `black_lake_crossing` | `blackglass_crossing` | active | Act 2 dungeon ID. |
| `forge_of_spells` | `meridian_forge` | active | Act 2 finale node and dungeon. |
| `conyberry_agatha` | `hushfen_pale_circuit` | alias active | Act 2 node alias. |
| `agathas_circuit` | `pale_circuit` | alias active | Act 2 dungeon alias. |

## Implementation Order

1. Centralize aliases in `dnd_game/data/id_aliases.py`.
2. Route quest, scene, flag, and map normalizers through that module.
3. Add save-load tests for a scene alias, quest alias, flag alias, map node alias, and new canonical scene input.
4. Rename dispatch keys in one act slice at a time.
5. After each slice, save from a migrated state and confirm the written `current_scene`, map state, quest IDs, and flags use target IDs.
6. Keep compatibility aliases after the full desktop pass.
7. Sync `android_port/` after desktop IDs, tests, and save fixtures are stable.

## Current Runtime Pass

Steps 1 through 4 are in the desktop runtime. The save roundtrip test now loads old scene, quest, flag, map node, and dungeon IDs, then confirms the rewritten save carries canonical IDs. The full Python test suite passed after the rename pass.

Next pass: update older prose docs, map-system markdown, and Android mirror strings after the desktop save contract stays quiet for one more sweep.
