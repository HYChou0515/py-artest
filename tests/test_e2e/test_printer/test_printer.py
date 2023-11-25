import itertools
import os
import shutil

import artest.artest
from artest.config import (
    set_message_formatter,
    set_printer,
    set_stringify_obj,
    set_test_case_id_generator,
)
from tests.helper import (
    assert_test_case_files_exist,
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

_message = []


def custom_printer(message):
    _message.append(message)


def custom_message_formatter(message_record):
    s = []
    if message_record.is_success:
        s.append(f"{'SUCCESS':10s}")
    else:
        s.append(f"{'FAIL':10s}")
    s.append(f"fc={message_record.fcid}")
    s.append(f"tc={message_record.tcid}")
    if message_record.message:
        s.append(f"msg={message_record.message}")
    s = " ".join(s)
    return f"custom: {s}"


def custom_stringify_obj(obj):
    return f"[{str(obj)}]"


dirname = os.path.dirname(__file__)


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, _tcid)
@make_cleanup_file(f"{dirname}/hello.py")
@make_callback(lambda: set_message_formatter(None))
@make_callback(lambda: set_printer(None))
@make_callback(lambda: _message.clear())
def test_custom_message_formatter():
    set_printer(custom_printer)
    set_message_formatter(custom_message_formatter)
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
    assert not results[0].is_success

    assert len(_message) == 2
    assert (
        _message[0]
        == f"custom: FAIL       fc={hello_id} tc=temp-test msg=Outputs not matched."
    )
    assert _message[1] == "Failed (0/1)"


@make_test_autoreg()
@make_cleanup_test_case_files(hello_id, _tcid)
@make_cleanup_file(f"{dirname}/hello2.py")
@make_callback(lambda: set_stringify_obj(None))
@make_callback(lambda: set_printer(None))
@make_callback(lambda: _message.clear())
def test_custom_stringify_obj():
    set_printer(custom_printer)
    set_stringify_obj(custom_stringify_obj)
    tcid = next(gen2)

    shutil.copy(f"{dirname}/hello.py.before", f"{dirname}/hello2.py")
    from .hello2 import hello  # noqa: E402

    hello("Hello", "World")

    assert_test_case_files_exist(hello_id, tcid)

    shutil.copy(f"{dirname}/hello.py.after", f"{dirname}/hello2.py")

    results = artest.artest.main()
    assert len(results) == 1
    assert results[0].fcid == hello_id
    assert results[0].tcid == tcid
    assert not results[0].is_success

    assert len(_message) == 2
    assert (
        _message[0]
        == f"ARTEST: FAIL       fc={hello_id} tc=temp-test msg=Outputs not matched. expected: return [Hello World!] actual: return [Hello World! This is a different string.]"
    )
    assert _message[1] == "Failed (0/1)"
