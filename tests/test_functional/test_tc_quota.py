import itertools
from collections import Counter

import artest.artest
from artest import autoreg
from artest.config import (
    reset_all_test_case_quota,
    set_test_case_id_generator,
    set_test_case_quota,
)
from artest.types import ConfigTestCaseQuota
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


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, None)
@make_cleanup_test_case_files(func2_id, None)
@make_cleanup_file(call_time_path(hello_id))
@make_cleanup_file(call_time_path(func2_id))
@make_callback(reset_all_test_case_quota)
def test_fc_tc_quota_max_count():
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

    test_results = artest.artest.main()

    assert len(test_results) == 5
    fcid_counter = Counter(tr.fcid for tr in test_results)
    assert fcid_counter[hello_id] == 3
    assert fcid_counter[func2_id] == 2

    assert {tr.tcid for tr in test_results} == {tcid[i] for i in range(5)}
    assert {tr.is_success for tr in test_results} == {True}

    assert get_call_time(hello_id) == 3
    assert get_call_time(func2_id) == 2


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, None)
@make_cleanup_file(call_time_path(hello_id))
@make_callback(reset_all_test_case_quota)
def test_tc_quota_max_count():
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

    test_results = artest.artest.main()

    assert len(test_results) == 2
    assert {tr.fcid for tr in test_results} == {hello_id}
    assert {tr.tcid for tr in test_results} == {tcid[0], tcid[1]}
    assert {tr.is_success for tr in test_results} == {True}

    assert get_call_time(hello_id) == 2
