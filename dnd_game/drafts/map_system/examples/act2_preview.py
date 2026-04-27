from __future__ import annotations

from ..data.act2_enemy_map import ACT2_ENEMY_DRIVEN_MAP
from ..runtime import DraftMapState, render_screen_with_rich


def main() -> None:
    state = DraftMapState(
        current_node_id="blackglass_relay_house",
        current_room_id="relay_gate",
        flags={
            "act2_started",
            "hushfen_truth_secured",
            "woodland_survey_cleared",
            "stonehollow_dig_cleared",
            "claims_meet_held",
            "iron_hollow_sabotage_resolved",
            "broken_prospect_cleared",
            "south_adit_cleared",
            "resonant_vault_reached",
            "quiet_choir_identified",
            "resonant_vault_outer_cleared",
            "blackglass_reached",
            "blackglass_crossed",
            "blackglass_relay_route_known",
        },
        flag_values={
            "act2_town_stability": 4,
            "act2_route_control": 3,
            "act2_whisper_pressure": 4,
            "act2_first_late_route": "south_adit",
        },
        active_quests={"sever_quiet_choir", "free_resonant_vault_captives"},
        visited_nodes={
            "iron_hollow_claims_council",
            "act2_expedition_hub",
            "hushfen_pale_circuit",
            "greywake_survey_camp",
            "stonehollow_dig",
            "act2_midpoint_convergence",
            "broken_prospect",
            "south_adit",
            "resonant_vault_outer_galleries",
            "blackglass_causeway",
            "blackglass_relay_house",
        },
        cleared_rooms={"causeway_lip", "far_landing"},
        seen_story_beats={"act2_midpoint_ready", "late_routes_open", "forge_route_confirmed", "blackglass_relay_found"},
    )
    dungeon = ACT2_ENEMY_DRIVEN_MAP.dungeons["blackglass_relay_house"]
    render_screen_with_rich(
        blueprint=ACT2_ENEMY_DRIVEN_MAP,
        state=state,
        dungeon=dungeon,
        player_name="Resonant Vaults Company",
        hp_text="61/78",
        gold=216,
        quest_text="Sever the Quiet Choir",
        act_text="Act 2",
        scene_text=(
            "The Act 2 map now shows the far-side relay branch between Blackglass and the Meridian Forge, "
            "where wet cable, timing slates, and the null bell can blunt Caldra's support line."
        ),
    )


if __name__ == "__main__":
    main()
