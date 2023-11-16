import itertools
from pickle import PicklingError

import pytest

from artest import autoreg, set_pickler
from artest.config import set_test_case_id_generator
from tests.helper import make_test_autoreg


def gen():
    while True:
        yield f"temp-test"


gen1, gen2 = itertools.tee(gen(), 2)

set_test_case_id_generator(gen1)

func_id = "d1ca94d298f849bdadb10dd80bb99a0b"


@autoreg(func_id)
def returns_some_lambda(n):
    return lambda x: x**3 + x**2 - 5 * x + n


@make_test_autoreg()
def test_standard_pickle_unpicklable():
    import pickle

    set_pickler(pickle)
    with pytest.raises(PicklingError) as exc_info:
        returns_some_lambda(5)
    assert "Can't pickle" in str(exc_info.value)
