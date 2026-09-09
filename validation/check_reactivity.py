"""One-parameter-at-a-time probes with explicit numerical invariants.

This is a synthetic contract check, not accuracy validation on real games.
Uses an isolated in-memory SQLite catalogue; does not touch the user's DB.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.database import Base
from app.schemas.catalog import ProjectProfile, ImplementationBaseline
from app.seed.seeder import seed_all
from app.seed.functions_data import GAME_FUNCTIONS
from app.services.recommender import build_recommendations

SAMPLES = {
    'name': 'Renamed', 'format': '2D', 'world_type': 'hub', 'scale': 'small', 'stage': 'release',
    'engine': 'unity', 'engine_version': '4.27', 'platforms': ['pc_linux'],
    'object_count_level': 'high', 'object_count': 50000, 'npc_count_level': 'high', 'npc_count': 5000,
    'player_count': 128, 'multiplayer': False, 'local_view_count': 4, 'functions': ['physics_simulation'],
    'target_resolution': '2160p', 'target_quality': 'low', 'target_fps': 144, 'render_api': 'dx11',
    'storage_type': 'hdd', 'memory_model': 'unified', 'upscaling_method': 'fsr', 'network_topology': 'lockstep',
    'frame_generation': True, 'base_render_fps': 30, 'streaming_pool_gb': 8,
    'draw_call_budget': 10000, 'simulation_radius_m': 1000, 'physics_tick_hz': 240,
    'audio_complexity': 'high', 'ram_limit_gb': 4, 'vram_limit_gb': 2, 'size_limit_gb': 1,
    'deadline_weeks': 2, 'complexity_tolerance': 1, 'priority': 'performance',
    'cpu_budget': 'low', 'gpu_budget': 'low', 'ram_budget': 'low', 'vram_budget': 'low',
}
RUNTIME_INVARIANT = {'name', 'stage', 'priority', 'cpu_budget', 'gpu_budget', 'ram_budget',
                     'vram_budget', 'deadline_weeks', 'complexity_tolerance', 'ram_limit_gb', 'vram_limit_gb',
                     'base_render_fps'}  # base FPS is dormant while frame_generation=False


def signature(result):
    h = result.hardware
    return {
        'requirements': {k: getattr(h, k) for k in ('required_cpu_index', 'required_gpu_index',
                         'estimated_ram_gb', 'estimated_vram_gb', 'estimated_draw_calls')},
        'subsystems': [x.model_dump() for x in h.cpu_subsystems + h.gpu_subsystems],
        'recommendations': {r.method_code: {'rank': r.rank, 'score': r.score,
                             'criteria': {c.key: c.raw for c in r.criteria}} for r in result.recommendations},
        'applicability': {r.method_code: r.excluded_reasons for r in result.excluded},
        'warnings': [r.model_dump() for r in result.risks] + h.caveats + h.modeling_gaps + h.unmet_limits,
        'transitions': [t.model_dump() for t in result.transitions],
    }


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert set(SAMPLES) == set(ProjectProfile.model_fields), 'Every current input must have a probe'
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_all(db, validate=False)
        base = ProjectProfile(functions=[f['code'] for f in GAME_FUNCTIONS], multiplayer=True, player_count=16,
                              render_api='dx12', world_type='open_world', stage='prototype')
        basket = ['physics_lod_sleeping', 'async_loading_pipeline', 'network_relevancy_priority']
        baseline = ImplementationBaseline(profile=base, basket=basket)
        reference = signature(build_recommendations(db, base, basket, baseline))
        rows = []
        for field, value in SAMPLES.items():
            profile = ProjectProfile.model_validate({**base.model_dump(), field: value})
            changed = signature(build_recommendations(db, profile, basket, baseline))
            differences = [domain for domain in reference if reference[domain] != changed[domain]]
            if field in RUNTIME_INVARIANT:
                assert reference['requirements'] == changed['requirements'], field
                assert reference['subsystems'] == changed['subsystems'], field
            if field == 'name':
                assert not differences, differences
            rows.append({'field': field, 'before': getattr(base, field), 'after': value,
                         'changed_domains': differences, 'runtime_invariant': field in RUNTIME_INVARIANT,
                         'requirements_before': reference['requirements'], 'requirements_after': changed['requirements']})
        out = ROOT / 'validation/technical-integration/reactivity.json'
        out.write_text(json.dumps({'synthetic': True, 'fields': len(rows), 'cases': rows}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(f'Checked {len(rows)} individual fields; {len(RUNTIME_INVARIANT)} runtime invariants passed.')
        for row in rows:
            print(row['field'] + ': ' + ', '.join(row['changed_domains']))


if __name__ == '__main__':
    main()
