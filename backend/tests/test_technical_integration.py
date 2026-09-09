import hashlib
import json
from pathlib import Path
import importlib.util

import pytest
from sqlalchemy import delete, select

from app.models.entities import Method, GameFunction, Conflict
from app.seed.technical_extensions import EFFECTS, FUNCTIONS
from app.seed.functions_data import GAME_FUNCTIONS
from app.seed.seeder import sync_function_taxonomy
from app.schemas.catalog import ProjectProfile
from app.services import hardware

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('party_review', ROOT / 'validation/integrate_parties.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


@pytest.mark.parametrize('code', ['atoms_microtransaction', 'choice_driven_endings',
                                  'branching_narrative_state_graph', 'ps5_release_2026'])
def test_nontechnical_decisions_never_become_hardware_features(code):
    assert review.classify(code, '| CPU GPU memory costs |', {})[:2] == ('excluded', None)


@pytest.mark.parametrize('code,function', [
    ('extended_destruction', 'destruction_simulation'), ('crowd_30000_npc', 'crowd_simulation'),
    ('1000_planets_landable', 'open_world_streaming'), ('64_player_multiplayer', 'multiplayer_netcode'),
    ('physics_based_hair_clothing', 'cloth_simulation'), ('hdr_lighting_story_moments', 'dynamic_lighting'),
])
def test_gameplay_requirements_with_technical_mechanisms_are_kept(code, function):
    status, mapped, _ = review.classify(code, '', {})
    assert status != 'excluded'
    assert mapped == function


def test_all_party_rows_are_traceable_and_no_game_claim_is_promoted():
    rows = json.loads((ROOT / 'validation/technical-integration/rows.json').read_text(encoding='utf-8'))
    profiles = json.loads((ROOT / 'validation/technical-integration/profiles.json').read_text(encoding='utf-8'))
    assert len(rows) == len({row['id'] for row in rows}) == 980
    assert len(profiles) == 58
    files = {p.name: p for p in ROOT.glob('партия-*.md')}
    assert len(files) == 11
    content = {name: path.read_text(encoding='utf-8').splitlines() for name, path in files.items()}
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in files.items()}
    for row in rows:
        assert content[row['file']][row['line']-1] == row['original']
        assert hashes[row['file']] == row['sha256']
        assert row['numerical_import'] is False
        assert row['game_adoption_verified'] is False
        if row['status'] == 'excluded':
            assert row['function'] is None
        else:
            assert row['function'] in {f['code'] for f in GAME_FUNCTIONS}
    # Match independently maintained historical enumeration, so a parser that
    # skips a table cannot manufacture complete coverage.
    prior = json.loads((ROOT / 'validation/research/simplified-2026-09-09/batch-coverage.json').read_text(encoding='utf-8'))
    assert {r['id'] for r in rows} == {r['row_id'] for r in prior}


def test_existing_sqlite_gets_extensions_without_overwriting_user_changes(db):
    codes = set(EFFECTS)
    functions = {row[0] for row in FUNCTIONS}
    db.execute(delete(Conflict).where(Conflict.a_code.in_(codes) | Conflict.b_code.in_(codes)))
    db.execute(delete(Method).where(Method.code.in_(codes)))
    db.execute(delete(GameFunction).where(GameFunction.code.in_(functions)))
    old = db.scalar(select(Method).where(Method.code == 'fixed_timestep_physics'))
    old.name = 'User edited name'
    db.flush()
    outcome = sync_function_taxonomy(db)
    assert outcome['technical_methods_created'] == len(codes)
    assert outcome['functions_created'] == len(functions)
    assert old.name == 'User edited name'
    new = db.scalar(select(Method).where(Method.code == 'portal_scene_capture_budget'))
    new.name = 'User portal implementation'
    db.flush()
    repeated = sync_function_taxonomy(db)
    assert repeated['technical_methods_created'] == repeated['technical_relations_created'] == 0
    assert new.name == 'User portal implementation'


@pytest.mark.parametrize('code', sorted(EFFECTS))
def test_new_methods_are_selectable_have_verification_and_explicit_model_effect(client, code):
    method = client.get('/api/catalog/methods/' + code).json()
    assert method['application_steps'] and method['verification_method'] and method['source_url']
    profile = ProjectProfile(functions=[method['function_code']], world_type='hub')
    result = client.post('/api/recommend', json={'profile': profile.model_dump(), 'basket': [code]}).json()
    assert code in result['accounted_method_codes']
    assert any(r['method_code'] == code for r in result['recommendations'])
    assert hardware.METHOD_SUBSYSTEM_EFFECTS[code]


@pytest.mark.parametrize('code,function', [
    ('hair_cards_lod', 'hair_rendering'), ('cloth_baked_animation', 'cloth_simulation'),
])
def test_local_representation_does_not_discount_entire_scene(db, code, function):
    profile = ProjectProfile(functions=[function, 'geometry_pipeline', 'physics_simulation'])
    method = db.scalar(select(Method).where(Method.code == code))
    original = hardware._load_indices(profile, [])
    selected = hardware._load_indices(profile, [method])
    assert selected['cpu_subsystem_load'] == original['cpu_subsystem_load']
    assert selected['gpu_subsystem_load'] == original['gpu_subsystem_load']


def test_physics_demand_affects_recommendation_criteria_and_chosen_work_is_not_erased(client):
    profile = ProjectProfile(functions=['physics_simulation'], physics_tick_hz=30)
    def run(p):
        response = client.post('/api/recommend', json={'profile': p.model_dump(), 'basket': ['fixed_timestep_physics']})
        assert response.status_code == 200
        return response.json()
    slow, fast = run(profile), run(profile.model_copy(update={'physics_tick_hz': 240}))
    def fit(result):
        method = next(r for r in result['recommendations'] if r['method_code'] == 'physics_lod_sleeping')
        return next(c['raw'] for c in method['criteria'] if c['key'] == 'resource_fit')
    assert fit(fast) > fit(slow)
    strict = run(profile.model_copy(update={'complexity_tolerance': 1}))
    assert strict['hardware']['required_cpu_index'] == slow['hardware']['required_cpu_index']
    assert 'fixed_timestep_physics' in strict['accounted_method_codes']
