import itertools

import artest.artest
from artest import autoreg, autostub
from artest.config import set_test_case_id_generator
from artest.types import OnFuncIdDuplicateAction, StatusTestResult
from tests.helper import (
    assert_test_case_files_exist,
    make_cleanup_test_case_files,
    make_test_autoreg,
)


def gen():
    i = 0
    while True:
        yield str(i)
        i += 1


@autostub("stub1", on_duplicate=OnFuncIdDuplicateAction.IGNORE)
def stub1():
    stub2(1)
    return "stub1"


@autostub("stub2", on_duplicate=OnFuncIdDuplicateAction.IGNORE)
def stub2(x):
    return x + 1


@autoreg("reg1", on_duplicate=OnFuncIdDuplicateAction.IGNORE)
def reg1():
    stub1()
    stub2(2)
    return "reg1"


@make_test_autoreg()
@make_cleanup_test_case_files("reg1")
@make_cleanup_test_case_files("stub1")
@make_cleanup_test_case_files("stub2")
def test_stub_counter():
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    tcid = next(gen2)

    reg1()

    assert_test_case_files_exist("reg1", tcid)

    test_results = artest.artest.main()

    assert len(test_results) == 1
    assert test_results[0].fcid == "reg1"
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS
