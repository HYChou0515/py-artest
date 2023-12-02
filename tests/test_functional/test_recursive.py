import itertools

import artest.artest
from artest import autoreg, autostub
from artest.config import set_test_case_id_generator
from tests.helper import (
    assert_test_case_files_exist,
    get_call_time,
    make_cleanup_file,
    make_cleanup_test_case_files,
    make_test_autoreg,
    set_call_time,
)

_tcid = "temp-test"


def gen():
    while True:
        yield _tcid


gen1, gen2 = itertools.tee(gen(), 2)

set_test_case_id_generator(gen1)

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


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, _tcid)
@make_cleanup_test_case_files(hello1_id, _tcid)
@make_cleanup_file(f"./{hello_id}.calltime.pkl")
@make_cleanup_file(f"./{hello1_id}.calltime.pkl")
@make_cleanup_file(f"./{stub_id}.calltime.pkl")
def test_recursive():
    set_call_time(hello1_id, 0)
    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    tcid = next(gen2)

    hello("Hello", "World")
    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(hello1_id) == 1  # called once by hello
    assert get_call_time(stub_id) == 3  # called once by hello, twice by hello1

    assert_test_case_files_exist(hello_id, tcid)
    assert_test_case_files_exist(hello1_id, tcid)

    set_call_time(hello1_id, 0)
    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 2
    assert {tr.fcid for tr in test_results} == {hello_id, hello1_id}
    assert {tr.tcid for tr in test_results} == {tcid}
    assert {tr.is_success for tr in test_results} == {True}

    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(hello1_id) == 2  # directly called + called once by hello
    assert get_call_time(stub_id) == 0  # stubed by artest, should not be called
