import itertools
import itertools as it

import artest.artest
from artest import autoreg
from artest.config import reset_all_test_case_quota, set_test_case_id_generator
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


gen1, gen2 = itertools.tee(gen(), 2)

set_test_case_id_generator(gen1)

fcid1 = "42927bbb9a2c4843acf5244b7ffca3de"
fcid2 = "d4cd1c718cc34bde86f28db3a51d8428"
fcid3 = "49e0161f4c744d9daf4afa3d913b1d68"


@autoreg(fcid1)
def func1(x):
    set_call_time(fcid1, get_call_time(fcid1) + 1)
    return x + 1


@autoreg(fcid2)
def func2(x):
    set_call_time(fcid2, get_call_time(fcid2) + 1)
    return x + 2


@autoreg(fcid3)
def func3(x):
    set_call_time(fcid3, get_call_time(fcid3) + 1)
    return x + 3


def setup_tcid():
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(fcid1, 0)
    set_call_time(fcid2, 0)
    set_call_time(fcid3, 0)

    tcid = [next(gen2) for _ in range(6)]

    assert func1(0) == 1
    assert func2(0) == 2
    assert func3(0) == 3
    assert func1(1) == 2
    assert func2(1) == 3
    assert get_call_time(fcid1) == 2
    assert get_call_time(fcid2) == 2
    assert get_call_time(fcid3) == 1

    assert_test_case_files_exist(fcid1, tcid[0])
    assert_test_case_files_exist(fcid2, tcid[1])
    assert_test_case_files_exist(fcid3, tcid[2])
    assert_test_case_files_exist(fcid1, tcid[3])
    assert_test_case_files_exist(fcid2, tcid[4])

    set_call_time(fcid1, 0)
    set_call_time(fcid2, 0)
    set_call_time(fcid3, 0)

    return tcid


@make_test_autoreg()
@make_cleanup_test_case_files(fcid1)
@make_cleanup_file(call_time_path(fcid1))
@make_cleanup_test_case_files(fcid2)
@make_cleanup_file(call_time_path(fcid2))
@make_cleanup_test_case_files(fcid3)
@make_cleanup_file(call_time_path(fcid3))
@make_callback(reset_all_test_case_quota)
def test_include_function():
    tcid = setup_tcid()

    test_results = artest.artest.main(
        ["--include-function", fcid1, "--include-function", fcid3]
    )

    assert len(test_results) == 5
    fc_group = {
        fcid: list(g)
        for fcid, g in it.groupby(
            sorted(test_results, key=lambda tr: tr.fcid), lambda tr: tr.fcid
        )
    }
    assert len(fc_group) == 3
    assert {tc.tcid for tc in fc_group[fcid1]} == {tcid[i] for i in [0, 3]}
    assert {tc.status == StatusTestResult.SUCCESS for tc in fc_group[fcid1]} == {True}
    assert {tc.tcid for tc in fc_group[fcid2]} == {tcid[1], tcid[4]}
    assert {tc.status == StatusTestResult.SKIP for tc in fc_group[fcid2]} == {True}
    assert {tc.tcid for tc in fc_group[fcid3]} == {tcid[2]}
    assert {tc.status == StatusTestResult.SUCCESS for tc in fc_group[fcid3]} == {True}

    assert get_call_time(fcid1) == 2
    assert get_call_time(fcid2) == 0
    assert get_call_time(fcid3) == 1


@make_test_autoreg()
@make_cleanup_test_case_files(fcid1)
@make_cleanup_file(call_time_path(fcid1))
@make_cleanup_test_case_files(fcid2)
@make_cleanup_file(call_time_path(fcid2))
@make_cleanup_test_case_files(fcid3)
@make_cleanup_file(call_time_path(fcid3))
@make_callback(reset_all_test_case_quota)
def test_exclude_function():
    tcid = setup_tcid()

    test_results = artest.artest.main(
        ["--exclude-function", fcid1, "--exclude-function", fcid3]
    )

    assert len(test_results) == 5
    fc_group = {
        fcid: list(g)
        for fcid, g in it.groupby(
            sorted(test_results, key=lambda tr: tr.fcid), lambda tr: tr.fcid
        )
    }
    assert len(fc_group) == 3
    assert {tc.tcid for tc in fc_group[fcid1]} == {tcid[i] for i in [0, 3]}
    assert {tc.status == StatusTestResult.SKIP for tc in fc_group[fcid1]} == {True}
    assert {tc.tcid for tc in fc_group[fcid2]} == {tcid[1], tcid[4]}
    assert {tc.status == StatusTestResult.SUCCESS for tc in fc_group[fcid2]} == {True}
    assert {tc.tcid for tc in fc_group[fcid3]} == {tcid[2]}
    assert {tc.status == StatusTestResult.SKIP for tc in fc_group[fcid3]} == {True}

    assert get_call_time(fcid1) == 0
    assert get_call_time(fcid2) == 2
    assert get_call_time(fcid3) == 0


@make_test_autoreg()
@make_cleanup_test_case_files(fcid1)
@make_cleanup_file(call_time_path(fcid1))
@make_cleanup_test_case_files(fcid2)
@make_cleanup_file(call_time_path(fcid2))
@make_cleanup_test_case_files(fcid3)
@make_cleanup_file(call_time_path(fcid3))
@make_callback(reset_all_test_case_quota)
def test_include_test_case():
    tcid = setup_tcid()

    test_results = artest.artest.main(
        ["--include-test-case", tcid[0], "--include-test-case", tcid[4]]
    )

    assert len(test_results) == 5
    fc_group = {
        fcid: list(g)
        for fcid, g in it.groupby(
            sorted(test_results, key=lambda tr: tr.fcid), lambda tr: tr.fcid
        )
    }
    assert len(fc_group) == 3
    assert {tc.tcid for tc in fc_group[fcid1]} == {tcid[i] for i in [0, 3]}
    assert fc_group[fcid1][0].status == StatusTestResult.SUCCESS
    assert fc_group[fcid1][1].status == StatusTestResult.SKIP
    assert {tc.tcid for tc in fc_group[fcid2]} == {tcid[1], tcid[4]}
    assert fc_group[fcid2][0].status == StatusTestResult.SKIP
    assert fc_group[fcid2][1].status == StatusTestResult.SUCCESS
    assert {tc.tcid for tc in fc_group[fcid3]} == {tcid[2]}
    assert fc_group[fcid3][0].status == StatusTestResult.SKIP

    assert get_call_time(fcid1) == 1
    assert get_call_time(fcid2) == 1
    assert get_call_time(fcid3) == 0


@make_test_autoreg()
@make_cleanup_test_case_files(fcid1)
@make_cleanup_file(call_time_path(fcid1))
@make_cleanup_test_case_files(fcid2)
@make_cleanup_file(call_time_path(fcid2))
@make_cleanup_test_case_files(fcid3)
@make_cleanup_file(call_time_path(fcid3))
@make_callback(reset_all_test_case_quota)
def test_exclude_test_case():
    tcid = setup_tcid()

    test_results = artest.artest.main(
        ["--exclude-test-case", tcid[0], "--exclude-test-case", tcid[4]]
    )

    assert len(test_results) == 5
    fc_group = {
        fcid: list(g)
        for fcid, g in it.groupby(
            sorted(test_results, key=lambda tr: tr.fcid), lambda tr: tr.fcid
        )
    }
    assert len(fc_group) == 3
    assert {tc.tcid for tc in fc_group[fcid1]} == {tcid[i] for i in [0, 3]}
    assert fc_group[fcid1][0].status == StatusTestResult.SKIP
    assert fc_group[fcid1][1].status == StatusTestResult.SUCCESS
    assert {tc.tcid for tc in fc_group[fcid2]} == {tcid[1], tcid[4]}
    assert fc_group[fcid2][0].status == StatusTestResult.SUCCESS
    assert fc_group[fcid2][1].status == StatusTestResult.SKIP
    assert {tc.tcid for tc in fc_group[fcid3]} == {tcid[2]}
    assert fc_group[fcid3][0].status == StatusTestResult.SUCCESS

    assert get_call_time(fcid1) == 1
    assert get_call_time(fcid2) == 1
    assert get_call_time(fcid3) == 1


@make_test_autoreg()
@make_cleanup_test_case_files(fcid1)
@make_cleanup_file(call_time_path(fcid1))
@make_cleanup_test_case_files(fcid2)
@make_cleanup_file(call_time_path(fcid2))
@make_cleanup_test_case_files(fcid3)
@make_cleanup_file(call_time_path(fcid3))
@make_callback(reset_all_test_case_quota)
def test_multi_args1():
    tcid = setup_tcid()

    test_results = artest.artest.main(
        ["--include-function", fcid1, "--exclude-test-case", tcid[0]]
    )

    assert len(test_results) == 5
    fc_group = {
        fcid: list(g)
        for fcid, g in it.groupby(
            sorted(test_results, key=lambda tr: tr.fcid), lambda tr: tr.fcid
        )
    }
    assert len(fc_group) == 3
    assert {tc.tcid for tc in fc_group[fcid1]} == {tcid[i] for i in [0, 3]}
    assert fc_group[fcid1][0].status == StatusTestResult.SKIP
    assert fc_group[fcid1][1].status == StatusTestResult.SUCCESS
    assert {tc.tcid for tc in fc_group[fcid2]} == {tcid[1], tcid[4]}
    assert fc_group[fcid2][0].status == StatusTestResult.SKIP
    assert fc_group[fcid2][1].status == StatusTestResult.SKIP
    assert {tc.tcid for tc in fc_group[fcid3]} == {tcid[2]}
    assert fc_group[fcid3][0].status == StatusTestResult.SKIP

    assert get_call_time(fcid1) == 1
    assert get_call_time(fcid2) == 0
    assert get_call_time(fcid3) == 0
