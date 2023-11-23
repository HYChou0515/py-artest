import itertools
from pickle import PicklingError

import pytest

from artest import autoreg
from artest.config import (
    set_assert_pickled_object_on_case_mode,
    set_on_pickle_dump_error,
    set_pickler,
    set_test_case_id_generator,
)
from tests.helper import make_cleanup_test_case_files, make_test_autoreg

_tcid = "temp-test"


def gen():
    while True:
        yield _tcid


gen1, gen2 = itertools.tee(gen(), 2)

set_test_case_id_generator(gen1)

func_id = "d1ca94d298f849bdadb10dd80bb99a0b"


@autoreg(func_id)
def returns_some_lambda(n):
    return lambda x: x**3 + x**2 - 5 * x + n


@make_test_autoreg()
@make_cleanup_test_case_files(func_id, _tcid)
def test_standard_pickle_unpicklable():
    import pickle

    set_pickler(pickle)

    returns_some_lambda(5)

    set_on_pickle_dump_error(PicklingError, "raise")
    with pytest.raises(PicklingError) as exc_info:
        returns_some_lambda(5)
    assert "Can't pickle" in str(exc_info.value)


@make_test_autoreg()
@make_cleanup_test_case_files(func_id, _tcid)
def test_good_when_serialize_bad_when_deserialize():
    import dill

    class BadPickler:
        def dumps(self, obj):
            return dill.dumps(obj)

        def loads(self, obj):
            raise ValueError("bad")

        def dump(self, obj, fp):
            return dill.dump(obj, fp)

        def load(self, fp):
            raise ValueError("bad")

    set_pickler(BadPickler())
    set_assert_pickled_object_on_case_mode(True)

    with pytest.raises(ValueError) as exc_info:
        returns_some_lambda(5)
    assert "bad" in str(exc_info.value)
