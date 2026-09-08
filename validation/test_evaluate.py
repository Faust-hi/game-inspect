"""Synthetic arithmetic checks; these do not validate hardware accuracy."""
import pytest

from evaluate import Prediction, Reference, compare


def reference(case='one', group='game', **changes):
    return Reference.model_validate(dict(case_id=case, game_group=group, split='test', kind='point',
        scale_id='synthetic', source='synthetic unit-test fixture', cpu_lower=100,
        cpu_upper=100, gpu_lower=100, gpu_upper=100, **changes))


def test_joint_tolerance_and_direction():
    old = Prediction(case_id='one', scale_id='synthetic', cpu=180, gpu=100)
    new = Prediction(case_id='one', scale_id='synthetic', cpu=160, gpu=30)
    result = compare([reference()], [old], [new])
    assert result['cases'][0]['baseline']['joint_within_70'] is False
    assert result['cases'][0]['candidate']['joint_within_70'] is True
    assert result['summaries']['test/point']['candidate']['gpu']['signed_mean'] == -.7


def test_missing_prediction_does_not_improve_coverage():
    prediction = Prediction(case_id='one', scale_id='synthetic', cpu=100, gpu=100)
    result = compare([reference()], [prediction], [])
    assert result['coverage']['paired_evaluated'] == 0
    assert result['summaries'] == {}


def test_game_weight_is_independent_of_scenario_count():
    refs = [reference('a1', 'A'), reference('a2', 'A'), reference('b', 'B')]
    values = [Prediction(case_id=ref.case_id, scale_id='synthetic', cpu=100 if ref.game_group=='A' else 200, gpu=100) for ref in refs]
    result = compare(refs, values, values)
    assert result['summaries']['test/point']['baseline']['joint_within_70'] == .5


def test_scale_mismatch_is_unevaluated():
    prediction = Prediction(case_id='one', scale_id='arbitrary_catalogue_index', cpu=1, gpu=1)
    result = compare([reference()], [prediction], [prediction])
    assert result['coverage']['unevaluated'] == 1


def test_partition_leakage_rejected():
    a, b = reference('a'), reference('b').model_copy(update={'split': 'train'})
    with pytest.raises(ValueError, match='leak'):
        compare([a, b], [], [])


def test_sufficient_hardware_does_not_establish_minimum():
    ref = reference().model_copy(update={'kind': 'sufficient', 'cpu_lower': None, 'gpu_lower': None})
    prediction = Prediction(case_id='one', scale_id='synthetic', cpu=1, gpu=10)
    result = compare([ref], [prediction], [prediction])
    assert 'test/point' not in result['summaries']
    assert result['cases'][0]['candidate']['cpu_relative_deviation'] == 0
