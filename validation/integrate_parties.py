"""Reproducible technical-scope review of every method row in all 11 parties.

Functional mapping is not semantic equivalence, proof of adoption in a game,
or a calibrated numerical effect. Original claims remain in the audit only.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.seed.methods_data import all_methods

# Ordered technical families, deliberately based on the stated mechanism.
# Gameplay without such a mechanism is not turned into a hardware factor.
FAMILIES = [
    ('destruction_simulation', r'destruc|dismember|fracture|debris|fortification'),
    ('portal_rendering', r'portal_render|stencil_portal|laser_dynamic_reflection|paintmap'),
    ('cloth_simulation', r'cloth|cape_animation'),
    ('hair_rendering', r'hair|tressfx|purehair'),
    ('path_tracing', r'path_trac|fully_ray_traced|rt_overdrive'),
    ('ray_traced_effects', r'ray_trac|raytrac|dxr_|ray_reconstruction'),
    ('upscaling_frame_generation', r'frame_generation|dlss|fsr_|super_sampling|supersampling|ubersampling'),
    ('split_screen_rendering', r'split.?screen|stereo_3d|oculus|vr_'),
    ('multiplayer_netcode', r'netcode|network|multiplayer|tickrate|tick_|_tick|subtick|lockstep|dedicated_server|server_author|server_tick|server_logic|instance_partition|cross_play|cross_platform_play|crossplay|_coop|coop_|cooperative|[0-9]+v[0-9]+|versus_8_player|max_[0-9]+_players|[0-9]+_players|player.*(?:sync|online)|format_6v6|bloodstain_player_messages|faction_war.*meta|operations_multi_map'),
    ('ai_pathfinding', r'pathfind|navmesh|navigation_constraint|find_in_sphere'),
    ('crowd_simulation', r'crowd|traffic_density|npc_settlement|settlement.*simulation|dense_ecosystem'),
    ('advanced_npc_ai', r'(^ai_|_ai_|_ai$|npc|npc_|_npcs|perception|director|spawn|enemy_tactics|ecology|provokable|simulation_distance|village_pillage_raid|settlement_building|dragon_encounter_random)'),
    ('vehicle_simulation', r'vehicle.*physics|car_physics|flight_simulation|horse_realtime|vehicle_combat'),
    ('water_simulation', r'water|wave_simulation|gerstner|fft_|planar_reflection'),
    ('physics_simulation', r'physics|physx|physical_sim|ragdoll|euphoria|euphobia|momentum|force_field|collision|gravity|fire_propagation|sleep_wake|environmental_hazard|hitbox|mtx_frame_rate_bug'),
    ('character_animation', r'animation|motion_capture|performance_capture|skinning|facs|skeletal|procedural_motion'),
    ('audio_system', r'audio|hrtf|reverb|sound_occlusion|sound_propag|dynamic_music|radio|voice_act|voice_over|voiced_|music_station|footsteps'),
    ('particle_systems', r'particle|volumetric_smoke'),
    ('volumetric_effects', r'volumetric|fog|weather|dust_storm|snowfall|tornado|night_cycle|day_night'),
    ('baked_lighting', r'lightmap|baked.*light|precomputed_static_lighting|normal_map_baked_ambient'),
    ('dynamic_global_illumination', r'global_illumination|voxel_gi|lighting_cache'),
    ('dynamic_shadows', r'shadow'),
    ('dynamic_lighting', r'lighting|light_shaft|illumination'),
    ('procedural_terrain', r'procedural_(?:world|planet|terrain|resource)|chunk.*generat'),
    ('procedural_vegetation', r'vegetation|trees|billboard|procedural_paris_buildings'),
    ('large_scale_terrain', r'terrain|tessell|tessel|parallax|displacement|megatexture|virtual_textur'),
    ('open_world_streaming', r'open_world|open_areas|open_levels|streaming|async_loading|chunk_render|world.*(?:scale|size)|planets_landable|paris_1_to_1|loading_screen|seamless_space|space_travel|hierarchical_lod|view_distance|rich_presence_landscape'),
    ('runtime_memory', r'32bit|64bit|x64|memory|_gc_|alloc|vram|ram_|gddr|texture_data'),
    ('render_scalability', r'resolution|quality_tier|4k_|4k60|fps|frame_budget|fov_|full_hd'),
    ('rendering_architecture', r'render|shader|culling|occlusion|compute|dx9|dx10|dx11|dx12|directx|vulkan|mantle|opengl|draw_call|thread|smt_|ecs_|entity_system|pso_|bump_normal|pbr|phong|fresnel|material|texture|specular|mesh|geometry|3d_skybox|hybrid_cpu|sodium_lithium|gtx_10_'),
    ('post_processing', r'postprocess|post_process|post_effect|depth_prepass|depth_of_field|bokeh|tone_map|color_grad|color_corr|film_grain|cubemap|screen_space_reflection|anti_alias'),
    ('save_system', r'save_|saving|savegame|snapshot'),
    ('build_delivery', r'differential_patch|vpk_|packed_assets|preload|directstorage'),
    ('project_architecture', r'engine|api_|client|mod_support|moddable|modding|mod_tools|workshop_mod|sdk|dll|ui_replace|ui_replacement|wiremod|level_editor|3d_editor|ui_minimal|physicalized_ui|physicalized_hud|lua_scripting'),
    ('runtime_security', r'anti_cheat|anticheat|anti_piracy|antipiracy|denuvo|drm|steam_required|launcher_required'),
    ('art_pipeline', r'photogrammetry|retopology|stylization|stylised|100000_photos'),
]
EXCLUDE = [
    ('monetization', r'monet|microtrans|subscription|business_model|free_to_play|f2p_|battle_pass|premium|paid_|_paid|loot_crate|loot_box|currency|membership|skin_economy|buyable|cosmetic|praxis_kit|atoms_|sales|copies|million_units|units_first|million_budget|refund'),
    ('narrative', r'narrative|story_branch|story_path|story_driven|story_orchestrat|choice_dialogue|choice_driven|dialogue_choice|dialogue_timed|ending|cliffhanger|writer_room|protagonist_choose|amorous|war_stories|questline|lore_|setting$|reincarnation'),
    ('release_event', r'^ps5_release|release_date|win_release|delisted|cancelled|pulled_from|exclusive$|post_launch_cleanup|post_launch_support|free_update|remaster_already|server_closure|shutdown$'),
]

# Individual review of technical rows whose names do not identify their mechanism.
OVERRIDES = {
    'lag_compensation_rewind': 'multiplayer_netcode', 'favor_the_shooter': 'multiplayer_netcode',
    'glicko_rating_competitive': 'multiplayer_netcode', 'ranked_matchmaking_added': 'multiplayer_netcode',
    'prime_matchmaking_2016': 'multiplayer_netcode', 'trust_factor_2017': 'runtime_security',
    'hdd_to_ssd_mandatory': 'open_world_streaming', 'interconnected_world_no_warping': 'open_world_streaming',
    'larger_zones_fewer_count': 'open_world_streaming', 'map_clustering_design': 'open_world_streaming',
    'java_17_21_migration': 'project_architecture', 'l4d_authoring_tools_2009': 'project_architecture',
    'procedural_megawad_snapmap': 'project_architecture', 'havok_behavior_toolset': 'character_animation',
    'leaning_curved_paths': 'character_animation', '4d_dissolve_transitions': 'character_animation',
    'infected_variation_24000': 'geometry_pipeline', 'layered_armor_system': 'geometry_pipeline',
    'motion_blur': 'post_processing', 'motion_blur_object_motion': 'post_processing',
    'hdr_bloom_2d_array': 'post_processing', 'hdr_display_support': 'post_processing',
    'hdr_pc_late': 'post_processing', 'hbao_horizon_based_ao': 'post_processing',
    'script_driven_companion_cover': 'advanced_npc_ai', 'mercenary_nemesis_system': 'advanced_npc_ai',
    'police_system_rework_2_0': 'advanced_npc_ai', 'eagle_senu_companion': 'advanced_npc_ai',
    'eagle_ikaros_companion': 'advanced_npc_ai', 'unprecedented_detail_simulation': 'physics_simulation',
    'bonfire_checkpoint_system': 'save_system', 'sites_of_grace_checkpoints': 'save_system',
    'no_hud_physicalized': 'project_architecture',
}


def classify(code, original, methods):
    for reason, pattern in EXCLUDE:
        if re.search(pattern, code, re.I):
            return 'excluded', None, reason
    if code in methods:
        return 'catalog_method', methods[code].get('function_code'), 'exact_code_is_not_game_adoption_evidence'
    if code in OVERRIDES:
        return 'technical_reference', OVERRIDES[code], 'individual_function_mapping_not_method_equivalence'
    for function, pattern in FAMILIES:
        if re.search(pattern, code, re.I):
            return 'technical_reference', function, 'function_mapping_not_method_equivalence'
    # A few gameplay descriptions have technical content only in the row body.
    if re.search(r'разруш|фрактур|обломк', original, re.I):
        return 'technical_requirement', 'destruction_simulation', 'explicit_destruction_requirement'
    if re.search(r'\b(?:NPC|ИИ)\b|симуляц|синхрониз|репликац', original, re.I):
        return 'technical_requirement', ('multiplayer_netcode' if re.search(r'синхрониз|репликац', original, re.I) else 'advanced_npc_ai'), 'explicit_simulation_requirement'
    return 'excluded', None, 'no_stated_architecture_compute_or_resource_mechanism'


def main():
    methods = {m['code']: m for m in all_methods()}
    rows, profiles = [], []
    for path in sorted(ROOT.glob('партия-*.md')):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        profile = None
        for line_no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if re.match(r'^## \d+[.)]', line):
                profile = {'id': f'{path.stem}:{line_no}', 'title': line.lstrip('# ').strip(),
                           'file': path.name, 'line': line_no, 'sha256': digest, 'technical_functions': [],
                           'metadata': [], 'evidence': 'unverified_game_profile'}
                profiles.append(profile)
            if profile is not None and line.startswith('- **'):
                profile['metadata'].append({'line': line_no, 'text': line})
            if not line.startswith('|') or profile is None:
                continue
            first = line.split('|')[1].strip().strip('`* ')
            match = re.match(r'^([A-Za-z0-9][A-Za-z0-9_]*(?:_[A-Za-z0-9]+)+)', first)
            if not match:
                continue
            code = match.group(1)
            status, function, reason = classify(code, line, methods)
            rows.append({'id': f'{path.stem}:{line_no}', 'profile_id': profile['id'],
                         'file': path.name, 'line': line_no, 'sha256': digest, 'code': code,
                         'original': line, 'status': status, 'function': function, 'reason': reason,
                         'numerical_import': False, 'game_adoption_verified': False,
                         'catalog_method': code if code in methods and status != 'excluded' else None})
            if function and function not in profile['technical_functions']:
                profile['technical_functions'].append(function)
    out = ROOT / 'validation/technical-integration'
    out.mkdir(exist_ok=True)
    for filename, value in [('rows.json', rows), ('profiles.json', profiles)]:
        (out / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    groups = {}
    for row in rows:
        if row['function']:
            groups.setdefault(row['function'], []).append({k: row[k] for k in ('id', 'code', 'profile_id', 'catalog_method')})
    summary = {'files': len(list(ROOT.glob('партия-*.md'))), 'profiles': len(profiles), 'rows': len(rows),
               'classification': dict(Counter(r['status'] for r in rows)),
               'excluded_reasons': dict(Counter(r['reason'] for r in rows if r['status'] == 'excluded')),
               'functions': {k: len(v) for k, v in sorted(groups.items())},
               'policy': 'Architecture, computational load or resources; no game-wide causal conclusions; no measured effect imported.'}
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # External research map, not a runtime game catalogue or calibration input.
    (out / 'function-map.json').write_text(
        json.dumps(groups, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
