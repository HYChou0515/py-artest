import io
import itertools

import artest.artest
from artest import autoreg, autostub
from artest.config import set_test_case_id_generator
from tests.helper import (
    assert_test_case_files_exist,
    get_call_time,
    make_cleanup_file,
    make_cleanup_test_case_files,
    make_test_autoreg,
    set_call_time,
)

_tcid = "temp-test"


def gen():
    while True:
        yield _tcid


gen1, gen2 = itertools.tee(gen(), 2)

set_test_case_id_generator(gen1)

hello_id = "7ea1cadf5f034540949a3b5e2ac12865"
stub_id = "6e435a4e5792483891074fb12af54672"


class Hello:
    @autoreg(hello_id)
    def hello(self, say, to):
        set_call_time(hello_id, get_call_time(hello_id) + 1)
        y = self.the_stub(io.StringIO("apple "))
        return f"{say} {to} {y}!"

    @autostub(stub_id)
    def the_stub(self, iox):
        iox.seek(0)
        x = iox.read()
        set_call_time(stub_id, get_call_time(stub_id) + 1)
        return x * 3


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, _tcid)
@make_cleanup_file(f"./{hello_id}.calltime.pkl")
@make_cleanup_file(f"./{stub_id}.calltime.pkl")
def test_class():
    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    tcid = next(gen2)

    hello = Hello()
    hello.hello("Hello", "World")
    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(stub_id) == 1  # called once by hello

    assert_test_case_files_exist(hello_id, tcid)

    set_call_time(hello_id, 0)
    set_call_time(stub_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 1
    assert test_results[0].fcid == hello_id
    assert test_results[0].tcid == tcid
    assert test_results[0].is_success

    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(stub_id) == 0  # stubed by artest, should not be called
