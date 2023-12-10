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


hello1_id = "7646bd27ad0d4380ba2a89b52859bff8"
hello_id = "8299dc17446a4c7fa759b979e780b346"
stub_id = "4642a810f82541d99dba373daaf85a29"


@autoreg(hello1_id)
def hello1(say, to):
    set_call_time(hello1_id, get_call_time(hello1_id) + 1)
    y1 = the_stub(10)
    y2 = the_stub(15)
    return f"{say} {to} {y1} {y2}!"


@autoreg(hello_id)
def hello(say, to):
    set_call_time(hello_id, get_call_time(hello_id) + 1)
    hello1(say, to)
    y = the_stub(5)
    return f"{say} {to} {y}!"


@autostub(stub_id)
def the_stub(x):
    set_call_time(stub_id, get_call_time(stub_id) + 1)
    return x**3 + x**2 - 5 * x + 1


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(fcid_list=[hello_id, hello1_id, stub_id])
def test_recursive(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(hello1_id, 0)
    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    tcid = [next(gen2) for _ in range(3)]

    hello("Hello", "World")
    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(hello1_id) == 1  # called once by hello
    assert get_call_time(stub_id) == 3  # called once by hello, twice by hello1

    assert_test_case_files_exist(hello_id, tcid[0])
    assert_test_case_files_exist(hello1_id, tcid[1])

    set_call_time(hello1_id, 0)
    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 2
    assert {tr.fcid for tr in test_results} == {hello_id, hello1_id}
    assert {tr.tcid for tr in test_results} == {tcid[0], tcid[1]}
    assert {tr.status == StatusTestResult.SUCCESS for tr in test_results} == {True}

    assert get_call_time(hello_id) == 1  # directly called
    assert (
        get_call_time(hello1_id) == 1 if enable_fastreg else 2
    )  # directly called + called once by hello
    assert get_call_time(stub_id) == 0  # stubbed by artest, should not be called
