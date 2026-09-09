"""Regression coverage for the fact-checked additions from proven-methods.md."""
import pytest
from sqlalchemy import delete, select

from app.models.entities import Conflict, Method
from app.schemas.catalog import ProjectProfile
from app.seed.methods_data import all_methods
from app.seed.reviewed_methods import EFFECTS, CONFLICTS
from app.seed.seeder import sync_function_taxonomy


def calculate(client, codes, baseline=None, **changes):
    data = {m['code']: m for m in all_methods()}
    profile = ProjectProfile(functions=sorted({data[c]['function_code'] for c in codes}),
                             multiplayer=True, player_count=16, network_topology='dedicated',
                             render_api='dx12', world_type='open_world')
    response = client.post('/api/recommend', json={
        'profile': profile.model_copy(update=changes).model_dump(), 'basket': codes, 'baseline': baseline,
    })
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize('code', sorted(EFFECTS))
def test_reviewed_method_surfaces_and_no_fictional_numerical_gain(client, code):
    result = calculate(client, [code])
    assert code in result['accounted_method_codes']
    assert any(row['method_code'] == code for row in result['recommendations'])
    card = client.get('/api/catalog/methods/' + code).json()
    assert card['source_url'].startswith('https://')
    assert card['application_steps'] and card['verification_method'] and card['limitations']
    # Keep the same function workload; only vary the selected implementation.
    reference = client.post('/api/recommend', json={'profile': result['profile'], 'basket': []}).json()
    for key in ('required_cpu_index', 'required_gpu_index', 'estimated_ram_gb', 'estimated_vram_gb'):
        assert result['hardware'][key] == reference['hardware'][key]
    assert card['requires_prototype'] is True


@pytest.mark.parametrize('code', ['lag_compensation_rewind', 'subtick_networking'])
@pytest.mark.parametrize('change', [{'multiplayer': False}, {'network_topology': 'lockstep'}])
def test_server_methods_do_not_leak_into_offline_or_pure_lockstep(client, code, change):
    result = calculate(client, [code], **change)
    assert code not in result['accounted_method_codes']
    assert any(row['method_code'] == code and row['excluded_reasons'] for row in result['excluded'])


def test_rewind_does_not_require_subtick_or_add_network_traffic(client):
    result = calculate(client, ['lag_compensation_rewind'])
    assert 'lag_compensation_rewind' in result['accounted_method_codes']
    card = client.get('/api/catalog/methods/lag_compensation_rewind').json()
    assert card['effect_scope'] == 'server'
    assert card['impact_network'] == 0


def test_directstorage_platform_and_fallback_conditions(client):
    windows_hdd = calculate(client, ['directstorage_io'], storage_type='hdd', render_api='dx11')
    assert 'directstorage_io' in windows_hdd['accounted_method_codes']
    rec = next(r for r in windows_hdd['recommendations'] if r['method_code'] == 'directstorage_io')
    assert any('CPU/системную память' in reason for reason in rec['reasons'])
    linux = calculate(client, ['directstorage_io'], platforms=['pc_linux'], render_api='vulkan')
    assert 'directstorage_io' not in linux['accounted_method_codes']
    mixed = calculate(client, ['directstorage_io'], platforms=['pc_windows', 'pc_linux'])
    assert 'directstorage_io' not in mixed['accounted_method_codes']


@pytest.mark.parametrize('api,applicable', [('dx11', False), ('opengl', False), ('dx12', True), ('vulkan', True)])
def test_async_compute_requires_explicit_queue_api(client, api, applicable):
    result = calculate(client, ['async_compute_overlap'], render_api=api)
    assert ('async_compute_overlap' in result['accounted_method_codes']) is applicable


@pytest.mark.parametrize('codes', [
    ['subtick_networking', 'tickrate_budgeting', 'lag_compensation_rewind'],
    ['ai_director_pacing', 'behaviour_tree_update_budget', 'npc_perception_budget'],
    ['directstorage_io', 'async_loading_pipeline', 'virtual_texturing', 'async_compute_overlap'],
])
def test_complementary_methods_can_coexist_and_do_not_replace_baseline(client, codes):
    before = calculate(client, codes[1:])
    baseline = {'profile': before['profile'], 'basket': codes[1:]}
    after = calculate(client, codes, baseline)
    assert set(codes) <= set(after['accounted_method_codes']), after['excluded']
    transition = next(t for t in after['transitions'] if t['method_code'] == codes[0])
    assert transition['status'] == 'new'
    assert transition['replaces'] == []


def test_saved_io_plan_reacts_to_storage_change_without_claiming_full_rewrite(client):
    before = calculate(client, ['directstorage_io'])
    baseline = {'profile': before['profile'], 'basket': ['directstorage_io']}
    retained = calculate(client, ['directstorage_io'], baseline, stage='release')
    transition = retained['transitions'][0]
    assert transition['status'] == 'retained' and transition['cost_max'] == 0
    changed = calculate(client, ['directstorage_io'], baseline, storage_type='hdd')
    transition = changed['transitions'][0]
    assert transition['status'] == 'adaptation'
    assert transition['cost_min'] == 0 < transition['cost_max']


def test_upgrade_adds_all_five_once_and_preserves_admin_edits(db):
    codes = set(EFFECTS)
    db.execute(delete(Conflict).where(Conflict.a_code.in_(codes) | Conflict.b_code.in_(codes)))
    db.execute(delete(Method).where(Method.code.in_(codes)))
    untouched = db.scalar(select(Method).where(Method.code == 'async_loading_pipeline'))
    untouched.name = 'Custom loading pipeline'
    db.flush()
    first = sync_function_taxonomy(db)
    assert first['technical_methods_created'] == 5
    assert first['technical_relations_created'] == len(CONFLICTS)
    row = db.scalar(select(Method).where(Method.code == 'directstorage_io'))
    row.summary = 'Local implementation'
    relation = db.scalar(select(Conflict).where(Conflict.a_code == 'directstorage_io'))
    relation.conflict_type = 'overlap'
    db.flush()
    second = sync_function_taxonomy(db)
    assert second['technical_methods_created'] == second['technical_relations_created'] == 0
    assert row.summary == 'Local implementation'
    assert relation.conflict_type == 'overlap'
    assert untouched.name == 'Custom loading pipeline'
    assert len(all_methods()) == len({m['code'] for m in all_methods()}) == 124


def test_verified_corrections_update_legacy_fields_preserving_custom_values(db):
    from app.seed.verified_corrections import FIELD_CHANGES, SOURCE_CHANGES, correct_existing
    from app.seed.sources import src
    for code, changes in FIELD_CHANGES.items():
        row = db.scalar(select(Method).where(Method.code == code))
        for field, (old, _) in changes.items():
            setattr(row, field, old)
    flow = db.scalar(select(Method).where(Method.code == 'flow_field_pathing'))
    flow.description = 'Admin-authored description'
    for code, (old_key, _) in SOURCE_CHANGES.items():
        row = db.scalar(select(Method).where(Method.code == code))
        old = src(old_key)
        row.source_url, row.source_title, row.source_date = old['url'], old['title'], old['date']
    db.flush()
    assert correct_existing(db) > 0
    assert flow.description == 'Admin-authored description'
    assert flow.pros == FIELD_CHANGES['flow_field_pathing']['pros'][1]
    assert flow.source_url == src('GAME_AI_FLOW_FIELDS')['url']
    assert correct_existing(db) == 0
