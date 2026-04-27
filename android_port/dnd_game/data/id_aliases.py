from __future__ import annotations


ACTIVE_SCENE_ID_ALIASES = {
    "neverwinter_briefing": "greywake_briefing",
    "phandalin_hub": "iron_hollow_hub",
    "high_road_liars_circle": "emberway_liars_circle",
    "high_road_false_checkpoint": "emberway_false_checkpoint",
    "high_road_false_tollstones": "emberway_false_tollstones",
    "old_owl_well": "blackglass_well",
    "wyvern_tor": "red_mesa_hold",
    "tresendar_manor": "duskmere_manor",
    "neverwinter_wood_survey_camp": "greywake_survey_camp",
    "wave_echo_outer_galleries": "resonant_vault_outer_galleries",
    "black_lake_causeway": "blackglass_causeway",
    "forge_of_spells": "meridian_forge",
    "conyberry_agatha": "hushfen_pale_circuit",
}

PLANNED_SCENE_ID_MIGRATIONS = {}

CANONICAL_TO_RUNTIME_SCENE_ID_ALIASES = {}

RUNTIME_SCENE_ID_ALIASES = {
    **ACTIVE_SCENE_ID_ALIASES,
}

QUEST_ID_ALIASES = {
    "restore_barthen_supplies": "restore_hadrik_supplies",
    "silence_old_owl_well": "silence_blackglass_well",
    "break_wyvern_tor_raiders": "break_red_mesa_raiders",
    "seek_agathas_truth": "seek_pale_witness_truth",
    "free_wave_echo_captives": "free_resonant_vault_captives",
}

PLANNED_QUEST_ID_MIGRATIONS = {}

ID_TEXT_REPLACEMENTS = (
    ("neverwinter_wood_survey_camp", "greywake_survey_camp"),
    ("neverwinter", "greywake"),
    ("phandalin", "iron_hollow"),
    ("high_road", "emberway"),
    ("old_owl_well", "blackglass_well"),
    ("old_owl", "blackglass_well"),
    ("wyvern_tor", "red_mesa_hold"),
    ("wyvern", "red_mesa"),
    ("tresendar_manor", "duskmere_manor"),
    ("tresendar", "duskmere"),
    ("wave_echo_outer_galleries", "resonant_vault_outer_galleries"),
    ("wave_echo", "resonant_vault"),
    ("black_lake_causeway", "blackglass_causeway"),
    ("black_lake_crossing", "blackglass_crossing"),
    ("black_lake", "blackglass"),
    ("forge_of_spells", "meridian_forge"),
)

FLAG_ID_ALIASES = {
    "briefing_q_neverwinter": "briefing_q_greywake",
    "briefing_q_phandalin": "briefing_q_iron_hollow",
    "phandelver_claims_council_seen": "iron_hollow_claims_council_seen",
    "phandalin_sabotage_resolved": "iron_hollow_sabotage_resolved",
    "act3_phandalin_state": "act3_iron_hollow_state",
    "agatha_truth_secured": "hushfen_truth_secured",
    "agatha_truth_clear": "pale_witness_truth_clear",
    "agatha_circuit_defiled": "hushfen_circuit_defiled",
    "agatha_claim_cover_suspected": "hushfen_claim_cover_suspected",
    "agatha_claim_cover_council_reaction_recorded": "hushfen_claim_cover_council_reaction_recorded",
    "agatha_public_warning_known": "pale_witness_public_warning_known",
    "agatha_warning_shared_publicly": "pale_witness_warning_shared_publicly",
    "agatha_warning_restricted": "pale_witness_warning_restricted",
    "agatha_warning_bound": "pale_witness_warning_bound",
    "agatha_bound_leverage": "pale_witness_bound_leverage",
    "agatha_pact_restraint_known": "pale_witness_pact_restraint_known",
    "agatha_circuit_entered": "pale_circuit_entered",
    "agatha_old_vow_named": "pale_circuit_old_vow_named",
    "agatha_waystone_heard": "pale_circuit_waystone_heard",
    "agatha_sigil_scrubbed": "pale_circuit_sigil_scrubbed",
    "quest_reward_agathas_clear_truth": "quest_reward_pale_witness_clear_truth",
    "dialogue_input_elira_hub_agatha_seen": "dialogue_input_elira_hub_hushfen_seen",
    "conyberry_circuit_strain": "hushfen_circuit_strain",
    "conyberry_pilgrims_steadied": "hushfen_pilgrims_steadied",
    "conyberry_clean_witness_taken": "hushfen_clean_witness_taken",
    "conyberry_whisper_track_named": "hushfen_whisper_track_named",
    "conyberry_first_site": "hushfen_first_site",
    "conyberry_cairn_ward_read": "hushfen_cairn_ward_read",
    "conyberry_cairn_grave_read": "hushfen_cairn_grave_read",
    "conyberry_cairn_trail_read": "hushfen_cairn_trail_read",
    "conyberry_chapel_seen": "hushfen_chapel_seen",
    "conyberry_chapel_relit": "hushfen_chapel_relit",
    "conyberry_field_lantern_taken": "hushfen_field_lantern_taken",
    "conyberry_chapel_quarantined": "hushfen_chapel_quarantined",
    "conyberry_grave_seen": "hushfen_grave_seen",
    "conyberry_grave_history_read": "hushfen_grave_history_read",
    "conyberry_dead_named": "hushfen_dead_named",
    "conyberry_claim_marks_found": "hushfen_claim_marks_found",
    "conyberry_sigil_seen": "hushfen_sigil_seen",
    "conyberry_sigil_broken": "hushfen_sigil_broken",
    "conyberry_sigil_copied": "hushfen_sigil_copied",
    "conyberry_watcher_baited": "hushfen_watcher_baited",
    "conyberry_watcher_seen": "hushfen_watcher_seen",
    "conyberry_second_site": "hushfen_second_site",
    "conyberry_two_sites_answered": "hushfen_two_sites_answered",
    "conyberry_warning_exit_choice": "hushfen_warning_exit_choice",
    "conyberry_chapel_pressure_payoff_applied": "hushfen_chapel_pressure_payoff_applied",
    "conyberry_chapel_sabotage_payoff": "hushfen_chapel_sabotage_payoff",
    "black_lake_conyberry_lamp_guidance": "blackglass_hushfen_lamp_guidance",
    "black_lake_conyberry_pressure_payoff": "blackglass_hushfen_pressure_payoff",
    "forge_conyberry_sigil_risk_applied": "forge_hushfen_sigil_risk_applied",
    "forge_conyberry_sigil_bound_safely": "forge_hushfen_sigil_bound_safely",
    "forge_conyberry_sigil_moral_risk": "forge_hushfen_sigil_moral_risk",
    "forge_lens_conyberry_sigil_used": "forge_lens_hushfen_sigil_used",
}

MAP_NODE_ID_ALIASES = {
    "neverwinter_briefing": "greywake_briefing",
    "high_road_ambush": "emberway_ambush",
    "phandalin_hub": "iron_hollow_hub",
    "old_owl_well": "blackglass_well",
    "wyvern_tor": "red_mesa_hold",
    "tresendar_manor": "duskmere_manor",
    "neverwinter_wood_survey_camp": "greywake_survey_camp",
    "wave_echo_outer_galleries": "resonant_vault_outer_galleries",
    "black_lake_causeway": "blackglass_causeway",
    "black_lake_crossing": "blackglass_crossing",
    "forge_of_spells": "meridian_forge",
    "phandalin_claims_council": "iron_hollow_claims_council",
    "phandalin_sabotage_night": "iron_hollow_sabotage_night",
    "conyberry_agatha": "hushfen_pale_circuit",
}

DUNGEON_ID_ALIASES = {
    "old_owl_well_dig": "blackglass_well_dig",
    "wyvern_tor_camp": "red_mesa_hold_assault",
    "tresendar_undercellars": "duskmere_undercellars",
    "tresendar_manor_ruins": "duskmere_manor_ruins",
    "wave_echo_outer_galleries": "resonant_vault_outer_galleries",
    "black_lake_crossing": "blackglass_crossing",
    "forge_of_spells": "meridian_forge",
    "agathas_circuit": "pale_circuit",
}


def _clean_id(raw_id: str | None) -> str | None:
    if raw_id is None:
        return None
    token = str(raw_id).strip()
    return token if token else token


def canonical_scene_id(scene_id: str | None) -> str | None:
    token = _clean_id(scene_id)
    if token is None:
        return None
    return ACTIVE_SCENE_ID_ALIASES.get(token, token)


def runtime_scene_id(scene_id: str | None) -> str | None:
    return canonical_scene_id(scene_id)


def canonical_quest_id(quest_id: str | None) -> str | None:
    token = _clean_id(quest_id)
    if token is None:
        return None
    return QUEST_ID_ALIASES.get(token, token)


def canonical_flag_id(flag_id: str | None) -> str | None:
    token = _clean_id(flag_id)
    if token is None:
        return None
    token = FLAG_ID_ALIASES.get(token, token)
    for old, new in ID_TEXT_REPLACEMENTS:
        token = token.replace(old, new)
    return token


def canonical_map_node_id(node_id: str | None) -> str | None:
    token = _clean_id(node_id)
    if token is None:
        return None
    token = MAP_NODE_ID_ALIASES.get(token, token)
    for old, new in ID_TEXT_REPLACEMENTS:
        token = token.replace(old, new)
    return token


def canonical_dungeon_id(dungeon_id: str | None) -> str | None:
    token = _clean_id(dungeon_id)
    if token is None:
        return None
    token = DUNGEON_ID_ALIASES.get(token, token)
    for old, new in ID_TEXT_REPLACEMENTS:
        token = token.replace(old, new)
    return token


def canonical_flag_value(value: object) -> object:
    if isinstance(value, str):
        return canonical_flag_id(value)
    return value


def canonicalize_flag_mapping(mapping: dict[str, object] | None) -> dict[str, object]:
    if not mapping:
        return {}
    normalized: dict[str, object] = {}
    for raw_key, value in mapping.items():
        key = canonical_flag_id(raw_key) if isinstance(raw_key, str) else raw_key
        if not isinstance(key, str):
            continue
        value = canonical_flag_value(value)
        if key in normalized and not normalized[key] and value:
            normalized[key] = value
            continue
        normalized.setdefault(key, value)
    return normalized
