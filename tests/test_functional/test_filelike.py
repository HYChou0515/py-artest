import io
import itertools

import artest.artest
from artest import autoreg, autostub
from artest.config import set_test_case_id_generator
from artest.types import StatusTestResult
from tests.helper import (
    assert_test_case_files_exist,
    call_time_path,
    get_call_time,
    make_callback,
    make_cleanup_file,
    make_cleanup_test_case_files,
    make_test_autoreg,
    set_call_time,
)


def gen():
    i = 0
    while True:
        yield str(i)
        i += 1


hello_id = "9cf9f5e5035e48c883374959379d0229"
stub_id = "327d0c57c4574d229c3c3a7e6c29cf49"


@autoreg(hello_id)
def hello(say, to):
    set_call_time(hello_id, get_call_time(hello_id) + 1)
    y = the_stub(io.StringIO("apple "))
    return f"{say} {to} {y}!"


@autostub(stub_id)
def the_stub(iox):
    iox.seek(0)
    x = iox.read()
    set_call_time(stub_id, get_call_time(stub_id) + 1)
    return x * 3


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id)
@make_cleanup_file(call_time_path(hello_id))
@make_cleanup_file(call_time_path(stub_id))
@make_callback(set_test_case_id_generator)
def test_filelike():
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

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
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(stub_id) == 0  # stubbed by artest, should not be called
