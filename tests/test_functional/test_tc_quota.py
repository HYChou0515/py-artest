import itertools

import artest.artest
from artest import autoreg
from artest.config import set_test_case_id_generator, set_test_case_quota
from tests.helper import (
    assert_test_case_files_exist,
    call_time_path,
    get_call_time,
    make_cleanup_file,
    make_cleanup_test_case_files,
    make_test_autoreg,
    set_call_time, make_callback,
)


def gen():
    i = 0
    while True:
        yield str(i)
        i += 1


hello_id = "a2d1462f1b1245019e1b4b9096f59d1b"


@autoreg(hello_id)
def hello(say, to):
    set_call_time(hello_id, get_call_time(hello_id) + 1)
    return f"{say} {to}"


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, None)
@make_cleanup_file(call_time_path(hello_id))
@make_callback(lambda: set_test_case_quota(max_count='inf'))
def _test_tc_quota_max_count():
    set_test_case_quota(max_count=2)

    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(hello_id, 0)

    tcid = [next(gen2) for _ in range(3)]

    hello("Hello", "World 1")
    hello("Hello", "World 2")
    hello("Hello", "World 3")
    assert get_call_time(hello_id) == 3  # directly called

    assert_test_case_files_exist(hello_id, tcid[0])
    assert_test_case_files_exist(hello_id, tcid[1])
    assert_test_case_files_exist(hello_id, tcid[2], assert_not_exist=True)

    set_call_time(hello_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 2
    assert {tr.fcid for tr in test_results} == {hello_id}
    assert {tr.tcid for tr in test_results} == {tcid[0], tcid[1]}
    assert {tr.is_success for tr in test_results} == {True}

    assert get_call_time(hello_id) == 2  # directly called
