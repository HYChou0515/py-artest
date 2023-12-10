import itertools

import pytest

import artest.artest
from artest import autoreg, autostub
from artest.config import set_test_case_id_generator
from artest.types import StatusTestResult
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


hello_id = "b5e47da9abc046eeac92ecff783e56f7"
hello2_id = "7711d7ad1b614b0bafec82b06e867d00"
hello3_id = "7eb5cb53de174839ace25a988f04a5c4"
stub_id = "4dfc86f1a6114a3a903cac3fbe32c57d"


@autoreg(hello_id)
def hello(say, to):
    set_call_time(hello_id, get_call_time(hello_id) + 1)
    raise ValueError("Hello")


@autoreg(hello2_id)
def hello2(say, to):
    set_call_time(hello2_id, get_call_time(hello2_id) + 1)
    the_stub(5)
    raise ValueError("Hello")


@autoreg(hello3_id)
def hello3(say, to):
    set_call_time(hello3_id, get_call_time(hello3_id) + 1)
    try:
        the_stub(5)
    except TypeError as err:
        return str(err)
    return None


@autostub(stub_id)
def the_stub(x):
    set_call_time(stub_id, get_call_time(stub_id) + 1)
    raise TypeError(f"Stub {x}")


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[hello_id, stub_id],
)
def test_autoreg_exception(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    tcid = next(gen2)

    with pytest.raises(ValueError) as err:
        hello("Hello", "World")
        assert str(err.value) == "Hello"

    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(stub_id) == 0  # called once by hello

    assert_test_case_files_exist(hello_id, tcid)

    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == hello_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(stub_id) == 0  # stubbed by artest, should not be called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[hello2_id, stub_id],
)
def test_autostub_exception(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(hello2_id, 0)
    set_call_time(stub_id, 0)

    tcid = next(gen2)

    with pytest.raises(TypeError) as err:
        hello2("Hello", "World")
        assert str(err.value) == "Hello"

    assert get_call_time(hello2_id) == 1  # directly called
    assert get_call_time(stub_id) == 1  # called once by hello

    assert_test_case_files_exist(hello2_id, tcid)

    set_call_time(hello2_id, 0)
    set_call_time(stub_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == hello2_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(hello2_id) == 1  # directly called
    assert get_call_time(stub_id) == 0  # stubbed by artest, should not be called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[hello3_id, stub_id],
)
def test_autostub_exception2(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(hello3_id, 0)
    set_call_time(stub_id, 0)

    tcid = next(gen2)

    hello3("Hello", "World")

    assert get_call_time(hello3_id) == 1  # directly called
    assert get_call_time(stub_id) == 1  # called once by hello

    assert_test_case_files_exist(hello3_id, tcid)

    set_call_time(hello3_id, 0)
    set_call_time(stub_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == hello3_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS
    assert get_call_time(hello3_id) == 1  # directly called
    assert get_call_time(stub_id) == 0  # stubbed by artest, should not be called
