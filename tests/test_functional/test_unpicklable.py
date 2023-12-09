import inspect
import itertools

import pytest

import artest
from artest import autoreg
from artest.config import (
    set_assert_pickled_object_on_case_mode,
    set_is_equal,
    set_on_pickle_dump_error,
    set_pickler,
    set_test_case_id_generator,
)
from artest.types import OnPickleDumpErrorAction, StatusTestResult
from tests.helper import (
    assert_test_case_files_exist,
    get_call_time,
    make_test_autoreg,
    set_call_time,
)


def gen():
    i = 0
    while True:
        yield str(i)
        i += 1


func_id = "d1ca94d298f849bdadb10dd80bb99a0b"
another_lambda_id = "67d1b3a8bb4a417a9cf2c70cf559b922"


@autoreg(func_id)
def returns_some_lambda(n):
    return lambda x: x**3 + x**2 - 5 * x + n


another_lambda = autoreg(another_lambda_id)(
    lambda x: x * 2
    + (
        0
        if (set_call_time(another_lambda_id, get_call_time(another_lambda_id) + 1))
        else 1
    )
)


@make_test_autoreg(fcid_list=[another_lambda_id])
def test_standard_pickle_unpicklable_function_should_pass():
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(another_lambda_id, 0)

    tcid = next(gen2)

    import pickle

    set_pickler(pickle)

    assert another_lambda(5) == 11
    assert get_call_time(another_lambda_id) == 1  # directly called

    assert_test_case_files_exist(another_lambda_id, tcid)

    set_call_time(another_lambda_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 1
    assert test_results[0].fcid == another_lambda_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(another_lambda_id) == 1  # directly called


@make_test_autoreg(fcid_list=[func_id])
def test_standard_pickle_unpicklable_output_should_fail():
    import pickle

    set_pickler(pickle)

    with pytest.warns(UserWarning) as record:
        returns_some_lambda(5)
        assert len(record.list) == 1
        assert "Can't pickle" in str(record.list[0].message)

    set_on_pickle_dump_error(AttributeError, OnPickleDumpErrorAction.RAISE)

    with pytest.raises(AttributeError) as exc_info:
        returns_some_lambda(5)

    assert "Can't pickle" in str(exc_info.value)


@make_test_autoreg(fcid_list=[func_id])
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


@make_test_autoreg(fcid_list=[func_id])
def test_good_when_serialize_good_when_deserialize():
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    _tcid = next(gen2)

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
    assert test_results[0].status == StatusTestResult.SUCCESS
