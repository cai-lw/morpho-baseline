import pytest
from evaluate import Evaluator

@pytest.fixture
def evaluator():
    reference = {
        '3sg.prs': {'get': 'gets', 'set': 'sets'},
        'pst': {'get': 'got', 'set': 'set'}
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
    prediction = {
        'one': {'get': 'gets'},
        'two': {'set': 'set'}
    }
    assert evaluator.score(prediction) == 2 / 3
