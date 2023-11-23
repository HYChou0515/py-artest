import itertools
import os
import shutil

import artest.artest
from artest.config import (
    set_function_root_path,
    set_is_equal,
    set_test_case_id_generator,
)
from tests.helper import (
    assert_test_case_files_exist,
    get_test_root_path,
    make_callback,
    make_cleanup_file,
    make_cleanup_test_case_files,
    make_test_autoreg,
)

from .hello_id import hello_id

_tcid = "temp-test"


def gen():
    while True:
        yield _tcid


gen1, gen2 = itertools.tee(gen(), 2)

set_test_case_id_generator(gen1)
set_function_root_path(get_test_root_path())

dirname = os.path.dirname(__file__)


def custom_is_equal(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a.startswith(b) or b.startswith(a)


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, _tcid)
@make_cleanup_file(f"{dirname}/hello.py")
@make_callback(lambda: set_is_equal(None))
def test_custom_equal():
    set_is_equal(custom_is_equal)
    tcid = next(gen2)

    shutil.copy(f"{dirname}/hello.py.before", f"{dirname}/hello.py")
    from .hello import hello  # noqa: E402

    hello("Hello", "World")

    assert_test_case_files_exist(hello_id, tcid)

    shutil.copy(f"{dirname}/hello.py.after", f"{dirname}/hello.py")

    results = artest.artest.main()
    assert len(results) == 1
    assert results[0].fcid == hello_id
    assert results[0].tcid == tcid
    assert results[0].is_success
