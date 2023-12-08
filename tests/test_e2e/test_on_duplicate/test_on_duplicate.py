import importlib
import itertools
import os

import pytest

import artest
from artest.config import set_on_func_id_duplicate, set_test_case_id_generator
from artest.types import OnFuncIdDuplicateAction, StatusTestResult
from tests.helper import assert_test_case_files_exist, make_test_autoreg

from .hello_id import dup_id, hello_id


def gen():
    i = 0
    while True:
        yield str(i)
        i += 1


dirname = os.path.dirname(__file__)


@make_test_autoreg(fcid_list=[hello_id])
def test_reload_hello_when_default_on_duplicate_action_is_ignore_should_pass():
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_on_func_id_duplicate(OnFuncIdDuplicateAction.IGNORE)
    from .hello import hello  # noqa: E402

    module = importlib.import_module(hello.__module__)
    importlib.reload(module)


@make_test_autoreg(fcid_list=[hello_id])
def test_reload_hello_should_fail():
    # reload hello.py should fail because hello_id is already registered in autoreg
    from .hello import hello  # noqa: E402

    module = importlib.import_module(hello.__module__)
    with pytest.raises(ValueError) as exec:
        importlib.reload(module)
    assert (
        exec.value.args[0] == f"Function {hello_id} is already registered in autoreg."
    )


@make_test_autoreg(fcid_list=[dup_id])
def test_dup_should_fail():
    with pytest.raises(ValueError) as exec:
        from .dup import dup1

        module = importlib.import_module(dup1.__module__)
        importlib.reload(module)
    assert exec.value.args[0] == f"Function {dup_id} is already registered in autoreg."


@make_test_autoreg(fcid_list=[dup_id])
def test_dup1_when_dup_action_is_ignored():
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_on_func_id_duplicate(OnFuncIdDuplicateAction.IGNORE)
    from .dup import dup1

    dup1(1)
    tcid = next(gen2)

    assert_test_case_files_exist(dup_id, tcid)

    results = artest.artest.main()
    assert len(results) == 1
    assert results[0].fcid == dup_id
    assert results[0].tcid == tcid
    assert results[0].status == StatusTestResult.SUCCESS


@make_test_autoreg(fcid_list=[dup_id])
def test_dup2_when_dup_action_is_ignored():
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_on_func_id_duplicate(OnFuncIdDuplicateAction.IGNORE)
    from .dup import dup2

    dup2(1)
    tcid = next(gen2)

    assert_test_case_files_exist(dup_id, tcid)

    results = artest.artest.main()
    assert len(results) == 1
    assert results[0].fcid == dup_id
    assert results[0].tcid == tcid

    # When you assign dup1 and dup2 to the same function id
    # with OnFuncIdDuplicateAction.IGNORE, the function will be
    # registered as dup1 (the first one).
    # So the result will be failed because the saved output is
    # from dup2.
    assert results[0].status == StatusTestResult.FAIL
    assert results[0].message == "Outputs not matched."
