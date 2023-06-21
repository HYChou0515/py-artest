import io
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
        yield f"temp-test"


gen1, gen2 = itertools.tee(gen(), 2)

set_test_case_id_generator(gen1)

hello_id = "9cf9f5e5035e48c883374959379d0229"
mock_id = "327d0c57c4574d229c3c3a7e6c29cf49"

hello_call_time = []
mock_call_time = []


@autoreg(hello_id)
def hello(say, to):
    hello_call_time.append(1)
    y = the_mock(io.StringIO("apple "))
    return f"{say} {to} {y}!"


@automock(mock_id)
def the_mock(iox):
    iox.seek(0)
    x = iox.read()
    mock_call_time.append(1)
    return x * 3


@make_test_autoreg()
def test_filelike():
    pop_all_from_list(hello_call_time)
    pop_all_from_list(mock_call_time)

    tcid = next(gen2)

    hello("Hello", "World")
    assert len(hello_call_time) == 1  # directly called
    assert len(mock_call_time) == 1  # called once by hello

    assert_test_case_files_exist(hello_id, tcid)

    pop_all_from_list(hello_call_time)
    pop_all_from_list(mock_call_time)

    artest.artest.main()

    assert len(hello_call_time) == 1  # directly called
    assert len(mock_call_time) == 0  # mocked by artest, should not be called
    cleanup_test_case_files(hello_id, tcid)
