import itertools
import os
import shutil

import artest.artest
from artest.config import set_test_case_id_generator
from tests.helper import (
    assert_test_case_files_exist,
    cleanup_test_case_files,
    make_test_autoreg,
)


def gen():
    while True:
        yield "temp-test"


gen1, gen2 = itertools.tee(gen(), 2)

set_test_case_id_generator(gen1)

dirname = os.path.dirname(__file__)


@make_test_autoreg()
def test_change_should_fail():
    tcid = next(gen2)

    shutil.copy(f"{dirname}/hello.py.before", f"{dirname}/hello.py")
    from hello import hello, hello_id  # noqa: E402

    hello("Hello", "World")

    assert_test_case_files_exist(hello_id, tcid)

    shutil.copy(f"{dirname}/hello.py.after", f"{dirname}/hello.py")
    from hello import hello  # noqa: E402

    results = artest.artest.main()
    assert len(results) == 1
    assert results[0].fcid == hello_id
    assert results[0].tcid == tcid
    assert not results[0].is_success

    os.remove(f"{dirname}/hello.py")
    cleanup_test_case_files(hello_id, tcid)
