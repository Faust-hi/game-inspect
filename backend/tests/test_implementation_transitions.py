"""A saved implementation changes migration effort, never the target runtime model."""
from types import SimpleNamespace

from app.schemas.catalog import ImplementationBaseline, ProjectProfile, input_fingerprint
from app.services import transitions

PROFILE = {"engine": "unreal", "stage": "prototype", "format": "3D",
           "functions": ["baked_lighting", "dynamic_global_illumination", "physics_simulation"],
           "world_type": "hub", "scale": "large"}


def request(client, basket, baseline=None, **patch):
    response = client.post('/api/recommend', json={"profile": {**PROFILE, **patch}, "basket": basket,
                                                  "baseline": baseline})
    assert response.status_code == 200, response.text
    return response.json()


def test_retained_solution_has_no_reimplementation_cost_at_later_stage(client):
    basket = ["lightmap_atlas_baking"]
    baseline = {"profile": PROFILE, "basket": basket}
    later = request(client, basket, baseline, stage="release")
    transition = next(t for t in later['transitions'] if t['method_code'] == basket[0])
    assert transition['status'] == 'retained'
    assert transition['cost_max'] == 0
    assert transition['complexity_max'] == 0
    recommendation = next(r for r in later['recommendations'] if r['method_code'] == basket[0])
    assert 'needs_rework' not in recommendation['flags']
    assert next(c['raw'] for c in recommendation['criteria'] if c['key'] == 'implementation_cost') == 0
    without = request(client, basket, stage="release")
    for field in ('required_cpu_index', 'required_gpu_index', 'estimated_ram_gb', 'estimated_vram_gb'):
        assert later['hardware'][field] == without['hardware'][field]
    assert later['input_key'] != without['input_key']


def test_replacement_uses_original_solution_and_new_hardware_only(client):
    baseline = {"profile": PROFILE, "basket": ["lightmap_atlas_baking"]}
    data = request(client, ["hardware_raytraced_gi"], baseline, stage="alpha")
    changed = next(t for t in data['transitions'] if t['method_code'] == 'hardware_raytraced_gi')
    assert changed['status'] == 'replacement'
    assert changed['replaces'] == ['lightmap_atlas_baking']
    assert changed['scope'] == 'subsystem_rework'
    assert changed['cost_max'] > changed['cost_min']
    assert any(t['status'] == 'removal' for t in data['transitions'])
    without = request(client, ["hardware_raytraced_gi"], stage="alpha")
    assert data['hardware']['required_gpu_index'] == without['hardware']['required_gpu_index']
    assert data['baseline']['basket'] == baseline['basket']


def test_changed_profile_requires_adaptation_but_name_does_not(client):
    baseline = {"profile": PROFILE, "basket": ["fixed_timestep_physics"]}
    same = request(client, baseline['basket'], baseline, name="Rename")
    assert same['transitions'][0]['status'] == 'retained'
    changed = request(client, baseline['basket'], baseline, physics_tick_hz=120)
    assert changed['transitions'][0]['status'] == 'adaptation'
    def physics_share(data):
        return next(s['share'] for s in data['hardware']['cpu_subsystems'] if s['label'].startswith('Физика'))
    assert physics_share(changed) > physics_share(same)
    # Another sequential CPU bottleneck may keep the required index unchanged.
    assert changed['hardware']['required_cpu_index'] >= same['hardware']['required_cpu_index']
    moved = request(client, baseline['basket'], baseline, engine="unity")
    assert moved['transitions'][0]['scope'] == 'architecture_migration'


def test_local_setting_replacement_and_dependency_chain_are_distinct():
    def method(code, level='setting'):
        return SimpleNamespace(code=code, implementation_cost=2, level=level, impact_gpu=0, impact_vram=0,
                               function=SimpleNamespace(code='physics_simulation'))
    profile = ProjectProfile(**PROFILE)
    baseline = ImplementationBaseline(profile=profile, basket=['old', 'dependent', 'indirect'])
    relations = [SimpleNamespace(a_code='new', b_code='old', conflict_type='alternative'),
                 SimpleNamespace(a_code='dependent', b_code='old', conflict_type='dependency'),
                 SimpleNamespace(a_code='indirect', b_code='dependent', conflict_type='dependency')]
    methods = {c: method(c) for c in ('new', 'old', 'dependent', 'indirect')}
    local = transitions.assess(methods['new'], profile, baseline, methods, relations)
    assert local.scope == 'local_adjustment'
    assert local.affected_methods == ['dependent', 'indirect']
    methods['new'].level = 'architecture'
    major = transitions.assess(methods['new'], profile, baseline, methods, relations)
    assert major.scope == 'subsystem_rework'
    assert major.cost_max > local.cost_max
    # A complement is not a replacement, even for the same function.
    relations[0].conflict_type = 'complement'
    assert not transitions.assess(methods['new'], profile, baseline, methods, relations).replaces


def test_retained_dependent_is_reassessed_when_its_prerequisite_is_removed():
    method = SimpleNamespace(code='dependent', implementation_cost=2, complexity=2, level='algorithm',
                             impact_gpu=0, impact_vram=0, function=SimpleNamespace(code='physics_simulation'))
    profile = ProjectProfile(**PROFILE)
    baseline = ImplementationBaseline(profile=profile, basket=['old', 'dependent'])
    relations = [SimpleNamespace(a_code='dependent', b_code='old', conflict_type='dependency')]
    result = transitions.assess(method, profile, baseline, {'dependent': method}, relations, ['dependent'])
    assert result.status == 'adaptation'
    assert result.scope == 'dependency_rework'
    assert result.affected_methods == ['old']
    assert result.cost_max > 0


def test_same_function_without_a_relation_is_only_a_possible_replacement():
    def method(code):
        return SimpleNamespace(code=code, implementation_cost=2, complexity=2, level='algorithm',
                               impact_gpu=0, impact_vram=0, function=SimpleNamespace(code='physics_simulation'))
    methods = {code: method(code) for code in ('old', 'new')}
    profile = ProjectProfile(**PROFILE)
    baseline = ImplementationBaseline(profile=profile, basket=['old'])
    result = transitions.assess(methods['new'], profile, baseline, methods, [], ['new'])
    assert result.status == 'possible_replacement'
    assert result.evidence == 'needs_interface_review'


def test_ranks_are_local_to_function_and_unrelated_function_does_not_change_them(client):
    single = request(client, [], functions=['water_simulation'])
    more = request(client, [], functions=['water_simulation', 'character_animation'])
    def water(data):
        return {r['method_code']: (r['rank'], r['score']) for r in data['recommendations']
                if r['function_code'] == 'water_simulation'}
    assert water(single) == water(more)
    assert all(r['function_code'] for r in more['recommendations'])


def test_baseline_fingerprint_is_canonical():
    p = ProjectProfile(**PROFILE)
    a = ImplementationBaseline(profile=p, basket=['b', 'a'])
    b = ImplementationBaseline(profile=p, basket=['a', 'b', 'b'])
    assert input_fingerprint(p, [], baseline=a) == input_fingerprint(p, [], baseline=b)
    assert input_fingerprint(p, [], baseline=a) != input_fingerprint(p, [])


def test_unknown_baseline_is_visible_and_invalid_shape_rejected(client):
    data = request(client, [], {"profile": PROFILE, "basket": ['missing']})
    assert any(r['code'] == 'unknown_baseline' for r in data['risks'])
    response = client.post('/api/recommend', json={"profile": PROFILE, "baseline": {"basket": [{}]}})
    assert response.status_code == 422
