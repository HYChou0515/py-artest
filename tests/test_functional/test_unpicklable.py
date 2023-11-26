import inspect
import itertools
from pickle import PicklingError

import pytest

import artest
from artest import autoreg
from artest._schema import OnPickleDumpErrorAction
from artest.config import (
    set_assert_pickled_object_on_case_mode,
    set_is_equal,
    set_on_pickle_dump_error,
    set_pickler,
    set_test_case_id_generator,
)
from tests.helper import (
    assert_test_case_files_exist,
    make_callback,
    make_cleanup_test_case_files,
    make_test_autoreg,
)

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

    set_on_pickle_dump_error(PicklingError, OnPickleDumpErrorAction.RAISE)
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


def custom_is_equal(a, b):
    if callable(a) and callable(b):
        return inspect.getsource(a) == inspect.getsource(b)


@make_test_autoreg()
@make_cleanup_test_case_files(func_id, _tcid)
@make_callback(lambda: set_is_equal(None))
def test_good_when_serialize_good_when_deserialize():
    set_is_equal(custom_is_equal)

    import dill

    class GoodPickler:
        def dumps(self, obj):
            return dill.dumps(obj)

        def loads(self, obj):
            return dill.loads(obj)

        def dump(self, obj, fp):
            return dill.dump(obj, fp)

        def load(self, fp):
            return dill.load(fp)

    set_pickler(GoodPickler())
    set_assert_pickled_object_on_case_mode(True)

    returns_some_lambda(5)

    assert_test_case_files_exist(func_id, _tcid)
    test_results = artest.artest.main()

    assert len(test_results) == 1
    assert test_results[0].fcid == func_id
    assert test_results[0].tcid == _tcid
    assert test_results[0].is_success
