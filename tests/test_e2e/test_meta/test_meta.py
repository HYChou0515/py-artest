import itertools
import os
import shutil

from artest.config import set_test_case_id_generator
from tests.helper import (
    assert_metadata_files_exist,
    assert_test_case_files_exist,
    make_test_autoreg,
)

from .hello_id import hello_id


def gen():
    i = 0
    while True:
        yield str(i)
        i += 1


dirname = os.path.dirname(__file__)


@make_test_autoreg(
    fcid_list=[hello_id],
    more_files_to_clean=[f"{dirname}/hello.py"],
)
def test_meta():
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    tcid = next(gen2)

    shutil.copy(f"{dirname}/hello.py.before", f"{dirname}/hello.py")
    from .hello import hello  # noqa: E402

    hello("Hello", "World")

    assert_test_case_files_exist(hello_id, tcid)
    assert_metadata_files_exist(hello_id, tcid)
