import io
import itertools
from functools import wraps

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
staticmethod_id = "ccfd4bde183f43f589b8b8bb80bbdda4"
static_caller_id = "80098e3731164b568032d333ae9ca04a"
property_id = "0a3efd01af67495b89c63c43f17bdc63"
decorator_id = "5cf078f0f42642c7a1a7c6283aa68c5b"
decorator_and_property_id = "afb995a2a5054062aa2add3ec0b84abb"


def custom_decorator(func):
    @wraps(func)
    def _wrapped(*args, **kwargs):
        kwargs["x"] += 1
        return func(*args, **kwargs)

    return _wrapped


def property_decorator(func):
    @wraps(func)
    def _wrapped(*args, **kwargs):
        x = func(*args, **kwargs)
        return x + 1

    return _wrapped


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

    @staticmethod
    @autoreg(staticmethod_id)
    def staticmethod(a, b):
        set_call_time(staticmethod_id, get_call_time(staticmethod_id) + 1)
        return a + b

    @autoreg(static_caller_id)
    def static_caller(self, x):
        set_call_time(static_caller_id, get_call_time(static_caller_id) + 1)
        return self.staticmethod(x, x + 10)

    @property
    @autoreg(property_id)
    def property_func(self):
        set_call_time(property_id, get_call_time(property_id) + 1)
        return "property"

    @autoreg(decorator_id)
    @custom_decorator
    def decorator(self, *, x):
        set_call_time(decorator_id, get_call_time(decorator_id) + 1)
        return x + 10

    @property
    @autoreg(decorator_and_property_id)
    @property_decorator
    def decorator_and_property(self):
        set_call_time(
            decorator_and_property_id, get_call_time(decorator_and_property_id) + 1
        )
        return 100


@make_test_autoreg()
@make_cleanup_test_case_files(decorator_and_property_id, _tcid)
@make_cleanup_file(f"./{decorator_and_property_id}.calltime.pkl")
def test_class_decorator_and_property():
    set_call_time(decorator_and_property_id, 0)

    tcid = next(gen2)

    hello = Hello()
    assert hello.decorator_and_property == 101
    assert get_call_time(decorator_and_property_id) == 1  # directly called

    assert_test_case_files_exist(decorator_and_property_id, tcid)

    set_call_time(decorator_and_property_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 1
    assert test_results[0].fcid == decorator_and_property_id
    assert test_results[0].tcid == tcid
    assert test_results[0].is_success

    assert get_call_time(decorator_and_property_id) == 1  # directly called


@make_test_autoreg()
@make_cleanup_test_case_files(decorator_id, _tcid)
@make_cleanup_file(f"./{decorator_id}.calltime.pkl")
def test_class_decorator():
    set_call_time(decorator_id, 0)

    tcid = next(gen2)

    hello = Hello()
    assert hello.decorator(x=10) == 21
    assert get_call_time(decorator_id) == 1  # directly called

    assert_test_case_files_exist(decorator_id, tcid)

    set_call_time(decorator_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 1
    assert test_results[0].fcid == decorator_id
    assert test_results[0].tcid == tcid
    assert test_results[0].is_success

    assert get_call_time(decorator_id) == 1  # directly called


@make_test_autoreg()
@make_cleanup_test_case_files(property_id, _tcid)
@make_cleanup_file(f"./{property_id}.calltime.pkl")
def test_class_property():
    set_call_time(property_id, 0)

    tcid = next(gen2)

    hello = Hello()
    assert hello.property_func == "property"
    assert get_call_time(property_id) == 1  # directly called

    assert_test_case_files_exist(property_id, tcid)

    set_call_time(property_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 1
    assert test_results[0].fcid == property_id
    assert test_results[0].tcid == tcid
    assert test_results[0].is_success

    assert get_call_time(property_id) == 1  # directly called


@make_test_autoreg()
@make_cleanup_test_case_files(staticmethod_id, _tcid)
@make_cleanup_test_case_files(static_caller_id, _tcid)
@make_cleanup_file(f"./{staticmethod_id}.calltime.pkl")
@make_cleanup_file(f"./{static_caller_id}.calltime.pkl")
def test_class_staticmethod_call():
    set_call_time(staticmethod_id, 0)
    set_call_time(static_caller_id, 0)

    tcid = next(gen2)

    hello = Hello()
    hello.static_caller(30)
    assert get_call_time(static_caller_id) == 1  # directly called
    assert get_call_time(staticmethod_id) == 1  # directly called

    assert_test_case_files_exist(static_caller_id, tcid)
    assert_test_case_files_exist(staticmethod_id, tcid)

    set_call_time(static_caller_id, 0)
    set_call_time(staticmethod_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 2
    assert {tr.fcid for tr in test_results} == {staticmethod_id, static_caller_id}
    assert {tr.tcid for tr in test_results} == {tcid}
    assert {tr.is_success for tr in test_results} == {True}

    assert get_call_time(staticmethod_id) == 2  # directly called
    assert get_call_time(static_caller_id) == 1  # directly called


@make_test_autoreg()
@make_cleanup_test_case_files(staticmethod_id, _tcid)
@make_cleanup_file(f"./{staticmethod_id}.calltime.pkl")
def test_class_staticmethod():
    set_call_time(staticmethod_id, 0)

    tcid = next(gen2)

    hello = Hello()
    hello.staticmethod(10, 20)
    assert get_call_time(staticmethod_id) == 1  # directly called

    assert_test_case_files_exist(staticmethod_id, tcid)

    set_call_time(staticmethod_id, 0)

    test_results = artest.artest.main()

    assert len(test_results) == 1
    assert test_results[0].fcid == staticmethod_id
    assert test_results[0].tcid == tcid
    assert test_results[0].is_success

    assert get_call_time(staticmethod_id) == 1  # directly called


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
    assert get_call_time(stub_id) == 0  # stubbed by artest, should not be called
