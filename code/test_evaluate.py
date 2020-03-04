import os
import pytest
from evaluate import Evaluator, load_reference, load_prediction, merge_identical_tags


@pytest.fixture
def evaluator():
    reference = {
        '3sg.prs': {'get': {'gets'}, 'set': {'sets'}},
        'pst': {'get': {'got'}, 'set': {'set'}}
    }
    return Evaluator(reference)


def test_basic(evaluator):
    prediction = {
        'one': {'get': 'get', 'set': 'set'},
        'two': {'get': 'gets', 'set': 'sets'}
    }
    assert evaluator.score(prediction) == 0.75


def test_different_number_of_tags(evaluator):
    # One tag with 1 accuracy. Returns 1 / max(1, 2) == 0.5
    prediction_1 = {
        'one': {'get': 'gets', 'set': 'sets'}
    }
    assert evaluator.score(prediction_1) == 0.5
    # Three tags with 1, 0.5, 0.5 accuracy.
    # Maximum match is 1.5. Returns 1.5 / max(2, 3) == 0.5
    prediction_3 = {
        'one': {'get': 'gets', 'set': 'sets'},
        'two': {'get': 'got', 'set': 'sot'},
        'three': {'get': 'get', 'set': 'set'}
    }
    assert evaluator.score(prediction_3) == 0.5


def test_missing_lemmas(evaluator):
    # Both tags has 1 accuracy and 0.5 recall. Returns the F1 score 2/3.
    prediction_less_lemmas = {
        'one': {'get': 'gets'},
        'two': {'set': 'set'}
    }
    assert evaluator.score(prediction_less_lemmas) == 2 / 3
    # Lemmas that don't appear in the reference is always considered wrong
    prediction_nonexistent_lemmas = {
        'one': {'get': 'gets', 'foo': 'bar'},
        'two': {'set': 'set', 'baz': 'quux'}
    }
    assert evaluator.score(prediction_nonexistent_lemmas) == 0.5


def test_multiple_truth():
    reference = {
        'pst': {'burn': {'burned', 'burnt'}, 'shrink': {'shrank', 'shrunk'}}
    }
    evaluator = Evaluator(reference)
    prediction = {
        'one': {'burn': 'burnt', 'shrink': 'shrunk'}
    }
    assert evaluator.score(prediction) == 1


def test_merge_identical_tags():
    reference = {
        '3sg.prs': {'get': {'gets'}, 'set': {'sets'}},
        'pst': {'get': {'got'}, 'set': {'set'}},
        'pst.ptcp': {'get': {'got'}, 'set': {'set'}}
    }
    reference = merge_identical_tags(reference)
    after_tags = frozenset(reference.keys())
    assert after_tags == {'3sg.prs', 'pst'} or after_tags == {'3sg.prs', 'pst.ptcp'}


def test_load(tmp_path):
    ref_file = os.path.join(tmp_path, 'test.gold')
    prd_file = os.path.join(tmp_path, 'test.pred')
    # The same test case as `test_basic`, but written to file
    with open(ref_file, 'w') as f:
        print('get', 'gets', '3sg.prs', sep='\t', file=f)
        print('get', 'got', 'pst', sep='\t', file=f)
        print('set', 'sets', '3sg.prs', sep='\t', file=f)
        print('set', 'set', 'pst', sep='\t', file=f)
    with open(prd_file, 'w') as f:
        print('get', 'gets', '3sg.prs', sep='\t', file=f)
        print('get', 'get', 'pst', sep='\t', file=f)
        print('set', 'sets', '3sg.prs', sep='\t', file=f)
        print('set', 'set', 'pst', sep='\t', file=f)
    evaluator = Evaluator(load_reference(ref_file))
    assert evaluator.score(load_prediction(prd_file)) == 0.75
    