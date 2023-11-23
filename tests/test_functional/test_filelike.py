import io
import itertools

import artest.artest
from artest import automock, autoreg
from artest.config import set_function_root_path, set_test_case_id_generator
from tests.helper import (
    assert_test_case_files_exist,
    get_call_time,
    get_test_root_path,
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
set_function_root_path(get_test_root_path())

hello_id = "9cf9f5e5035e48c883374959379d0229"
mock_id = "327d0c57c4574d229c3c3a7e6c29cf49"


@autoreg(hello_id)
def hello(say, to):
    set_call_time(hello_id, get_call_time(hello_id) + 1)
    y = the_mock(io.StringIO("apple "))
    return f"{say} {to} {y}!"


@automock(mock_id)
def the_mock(iox):
    iox.seek(0)
    x = iox.read()
    set_call_time(mock_id, get_call_time(mock_id) + 1)
    return x * 3


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, _tcid)
@make_cleanup_file(f"./{hello_id}.calltime.pkl")
@make_cleanup_file(f"./{mock_id}.calltime.pkl")
def test_filelike():
    set_call_time(hello_id, 0)
    set_call_time(mock_id, 0)

    tcid = next(gen2)

    hello("Hello", "World")
    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(mock_id) == 1  # called once by hello

    assert_test_case_files_exist(hello_id, tcid)

    set_call_time(hello_id, 0)
    set_call_time(mock_id, 0)

    artest.artest.main()

    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(mock_id) == 0  # mocked by artest, should not be called
