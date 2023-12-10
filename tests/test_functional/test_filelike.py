import io
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


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[hello_id, stub_id],
)
def test_filelike(enable_fastreg):
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

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == hello_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(stub_id) == 0  # stubbed by artest, should not be called
