import itertools

import artest.artest
from artest import automock, autoreg
from artest.config import set_test_case_id_generator
from tests.helper import (
    assert_test_case_files_exist,
    cleanup_test_case_files,
    make_test_autoreg,
    pop_all_from_list,
)


def gen():
    while True:
        yield "temp-test"


gen1, gen2 = itertools.tee(gen(), 2)

set_test_case_id_generator(gen1)

hello1_id = "7646bd27ad0d4380ba2a89b52859bff8"
hello_id = "8299dc17446a4c7fa759b979e780b346"
mock_id = "4642a810f82541d99dba373daaf85a29"
hello1_call_time = []
hello_call_time = []
mock_call_time = []


@autoreg(hello1_id)
def hello1(say, to):
    hello1_call_time.append(1)
    y1 = the_mock(10)
    y2 = the_mock(15)
    return f"{say} {to} {y1} {y2}!"


@autoreg(hello_id)
def hello(say, to):
    hello_call_time.append(1)
    hello1(say, to)
    y = the_mock(5)
    return f"{say} {to} {y}!"


@automock(mock_id)
def the_mock(x):
    mock_call_time.append(1)
    return x**3 + x**2 - 5 * x + 1


@make_test_autoreg()
def test_recursive():
    pop_all_from_list(hello1_call_time)
    pop_all_from_list(hello_call_time)
    pop_all_from_list(mock_call_time)

    tcid = next(gen2)

    hello("Hello", "World")
    assert len(hello_call_time) == 1  # directly called
    assert len(hello1_call_time) == 1  # called once by hello
    assert len(mock_call_time) == 3  # called once by hello, twice by hello1

    assert_test_case_files_exist(hello_id, tcid)
    assert_test_case_files_exist(hello1_id, tcid)

    pop_all_from_list(hello1_call_time)
    pop_all_from_list(hello_call_time)
    pop_all_from_list(mock_call_time)

    artest.artest.main()
    assert len(hello_call_time) == 1  # directly called
    assert len(hello1_call_time) == 2  # directly called + called once by hello
    assert len(mock_call_time) == 0  # mocked by artest, should not be called

    cleanup_test_case_files(hello_id, tcid)
    cleanup_test_case_files(hello1_id, tcid)
