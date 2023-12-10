import itertools
from collections import Counter

import pytest

import artest.artest
from artest import autoreg
from artest.config import set_test_case_id_generator, set_test_case_quota
from artest.types import ConfigTestCaseQuota, StatusTestResult
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


hello_id = "a2d1462f1b1245019e1b4b9096f59d1b"
func2_id = "d8d990ad4e7b46a2a3b8da29acd00710"


@autoreg(hello_id)
def hello(say, to):
    set_call_time(hello_id, get_call_time(hello_id) + 1)
    return f"{say} {to}"


@autoreg(func2_id, quota=ConfigTestCaseQuota(max_count=2))
def func2(x):
    set_call_time(func2_id, get_call_time(func2_id) + 1)
    return x + 1


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[hello_id, func2_id],
)
def test_fc_tc_quota_max_count(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(hello_id, 0)

    tcid = [next(gen2) for _ in range(6)]

    hello("Hello", "World 1")
    hello("Hello", "World 2")
    hello("Hello", "World 3")
    func2(1)
    func2(2)
    func2(3)
    assert get_call_time(hello_id) == 3
    assert get_call_time(func2_id) == 3

    assert_test_case_files_exist(hello_id, tcid[0])
    assert_test_case_files_exist(hello_id, tcid[1])
    assert_test_case_files_exist(hello_id, tcid[2])
    assert_test_case_files_exist(func2_id, tcid[3])
    assert_test_case_files_exist(func2_id, tcid[4])
    assert_test_case_files_exist(func2_id, tcid[5], assert_not_exist=True)

    set_call_time(hello_id, 0)
    set_call_time(func2_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 5
    fcid_counter = Counter(tr.fcid for tr in test_results)
    assert fcid_counter[hello_id] == 3
    assert fcid_counter[func2_id] == 2

    assert {tr.tcid for tr in test_results} == {tcid[i] for i in range(5)}
    assert {tr.status == StatusTestResult.SUCCESS for tr in test_results} == {True}

    assert get_call_time(hello_id) == 3
    assert get_call_time(func2_id) == 2


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[hello_id],
)
def test_tc_quota_max_count(enable_fastreg):
    set_test_case_quota(max_count=2)

    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(hello_id, 0)

    tcid = [next(gen2) for _ in range(3)]

    hello("Hello", "World 1")
    hello("Hello", "World 2")
    hello("Hello", "World 3")
    assert get_call_time(hello_id) == 3

    assert_test_case_files_exist(hello_id, tcid[0])
    assert_test_case_files_exist(hello_id, tcid[1])
    assert_test_case_files_exist(hello_id, tcid[2], assert_not_exist=True)

    set_call_time(hello_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 2
    assert {tr.fcid for tr in test_results} == {hello_id}
    assert {tr.tcid for tr in test_results} == {tcid[0], tcid[1]}
    assert {tr.status == StatusTestResult.SUCCESS for tr in test_results} == {True}

    assert get_call_time(hello_id) == 2
