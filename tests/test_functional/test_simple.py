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

hello_id = "a5f4cb0ffd914782b35988d25523734b"
stub_id = "b7e21c5a7dcf4ccb96eb37e1bbfe2c28"


@autoreg(hello_id)
def hello(say, to):
    set_call_time(hello_id, get_call_time(hello_id) + 1)
    y = the_stub(5)
    return f"{say} {to} {y}!"


@autostub(stub_id)
def the_stub(x):
    set_call_time(stub_id, get_call_time(stub_id) + 1)
    return x**3 + x**2 - 5 * x + 1


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, _tcid)
@make_cleanup_file(f"./{hello_id}.calltime.pkl")
@make_cleanup_file(f"./{stub_id}.calltime.pkl")
def test_simple():
    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    tcid = next(gen2)

    hello("Hello", "World")
    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(stub_id) == 1  # called once by hello

    assert_test_case_files_exist(hello_id, tcid)

    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 1
    assert test_results[0].fcid == hello_id
    assert test_results[0].tcid == tcid
    assert test_results[0].is_success

    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(stub_id) == 0  # stubed by artest, should not be called
