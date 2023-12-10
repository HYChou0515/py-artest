import io
import itertools
from functools import wraps

import pytest

import artest.artest
from artest import autoreg, autostub
from artest.config import set_test_case_id_generator
from artest.types import StatusTestResult
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


hello_id = "hello_id-7ea1cadf5f034540949a3b5e2ac12865"
stub_id = "stub_id-6e435a4e5792483891074fb12af54672"
staticmethod_id = "staticmethod_id-ccfd4bde183f43f589b8b8bb80bbdda4"
static_caller_id = "static_caller_id-80098e3731164b568032d333ae9ca04a"
property_id = "property_id-0a3efd01af67495b89c63c43f17bdc63"
decorator_id = "decorator_id-5cf078f0f42642c7a1a7c6283aa68c5b"
decorator2_id = "decorator2_id-2fa94dbc6f5d42198ecbb140e013caad"
decorator3_id = "decorator3_id-55a09978ce314120abb31506d89672db"
decorator_and_property_id = "decorator_and_property_id-afb995a2a5054062aa2add3ec0b84abb"
classmethod_id = "classmethod_id-d9ee01b913694410aaa5c0a432199068"


def custom_decorator(func):
    @wraps(func)
    def _wrapped(*args, **kwargs):
        kwargs["x"] += 1
        return func(*args, **kwargs)

    return _wrapped


def custom_decorator2(func):
    @wraps(func)
    def _wrapped(*args, **kwargs):
        x = func(*args, **kwargs)
        return x + 1

    return _wrapped


def custom_decorator3(func):
    @wraps(func)
    def _wrapped(*args, **kwargs):
        kwargs["x"] += 10
        x = func(*args, **kwargs)
        kwargs["x"] = x
        x = func(*args, **kwargs)
        kwargs["x"] = x
        x = func(*args, **kwargs)
        return x + 29

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

    @classmethod
    @autoreg(classmethod_id)
    def class_method(cls, a, b):
        set_call_time(classmethod_id, get_call_time(classmethod_id) + 1)
        return a + b + 30

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
    @custom_decorator2
    def decorator_and_property(self):
        set_call_time(
            decorator_and_property_id, get_call_time(decorator_and_property_id) + 1
        )
        return 100

    @autoreg(decorator2_id)
    @custom_decorator2
    def decorator2(self, x):
        set_call_time(decorator2_id, get_call_time(decorator2_id) + 1)
        return x + 10

    @autoreg(decorator3_id)
    @custom_decorator3
    def decorator3(self, *, x):
        set_call_time(decorator3_id, get_call_time(decorator3_id) + 1)
        return self.decorator_and_property + x * self.decorator2(
            self.decorator_and_property
        )


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[classmethod_id],
)
def test_class_class_method(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(classmethod_id, 0)

    tcid = next(gen2)

    assert Hello.class_method(20, 15) == 65
    assert get_call_time(classmethod_id) == 1  # directly called

    assert_test_case_files_exist(classmethod_id, tcid)

    set_call_time(classmethod_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == classmethod_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(classmethod_id) == 1  # directly called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[decorator3_id, decorator2_id, decorator_and_property_id],
)
def test_class_decorator3(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(decorator3_id, 0)
    set_call_time(decorator2_id, 0)
    set_call_time(decorator_and_property_id, 0)

    tcid = [next(gen2) for _ in range(10)]

    hello = Hello()
    assert hello.decorator3(x=11) == 30781874
    assert get_call_time(decorator3_id) == 3  # directly called

    assert_test_case_files_exist(decorator3_id, tcid[0])

    set_call_time(decorator3_id, 0)
    set_call_time(decorator2_id, 0)
    set_call_time(decorator_and_property_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 10
    counts_by_fcid = {tr.fcid: 0 for tr in test_results}
    for tr in test_results:
        counts_by_fcid[tr.fcid] += 1
    assert counts_by_fcid[decorator3_id] == 1
    assert counts_by_fcid[decorator2_id] == 3
    assert counts_by_fcid[decorator_and_property_id] == 6

    assert {tr.tcid for tr in test_results} == set(tcid)
    assert {tr.status == StatusTestResult.SUCCESS for tr in test_results} == {True}

    assert get_call_time(decorator3_id) == 3  # directly called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[decorator2_id],
)
def test_class_decorator2(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(decorator2_id, 0)

    tcid = next(gen2)

    hello = Hello()
    assert hello.decorator2(20) == 31
    assert get_call_time(decorator2_id) == 1  # directly called

    assert_test_case_files_exist(decorator2_id, tcid)

    set_call_time(decorator2_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == decorator2_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(decorator2_id) == 1  # directly called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[decorator_and_property_id],
)
def test_class_decorator_and_property(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(decorator_and_property_id, 0)

    tcid = next(gen2)

    hello = Hello()
    assert hello.decorator_and_property == 101
    assert get_call_time(decorator_and_property_id) == 1  # directly called

    assert_test_case_files_exist(decorator_and_property_id, tcid)

    set_call_time(decorator_and_property_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == decorator_and_property_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(decorator_and_property_id) == 1  # directly called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[decorator_id],
)
def test_class_decorator(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(decorator_id, 0)

    tcid = next(gen2)

    hello = Hello()
    assert hello.decorator(x=10) == 21
    assert get_call_time(decorator_id) == 1  # directly called

    assert_test_case_files_exist(decorator_id, tcid)

    set_call_time(decorator_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == decorator_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(decorator_id) == 1  # directly called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[property_id],
)
def test_class_property(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(property_id, 0)

    tcid = next(gen2)

    hello = Hello()
    assert hello.property_func == "property"
    assert get_call_time(property_id) == 1  # directly called

    assert_test_case_files_exist(property_id, tcid)

    set_call_time(property_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == property_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(property_id) == 1  # directly called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[staticmethod_id, static_caller_id],
)
def test_class_staticmethod_call(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(staticmethod_id, 0)
    set_call_time(static_caller_id, 0)

    tcid1 = next(gen2)
    tcid2 = next(gen2)

    hello = Hello()
    hello.static_caller(30)
    assert get_call_time(static_caller_id) == 1  # directly called
    assert get_call_time(staticmethod_id) == 1  # directly called

    assert_test_case_files_exist(static_caller_id, tcid1)
    assert_test_case_files_exist(staticmethod_id, tcid2)

    set_call_time(static_caller_id, 0)
    set_call_time(staticmethod_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 2
    assert {tr.fcid for tr in test_results} == {staticmethod_id, static_caller_id}
    assert {tr.tcid for tr in test_results} == {tcid1, tcid2}
    assert {tr.status == StatusTestResult.SUCCESS for tr in test_results} == {True}

    assert (
        get_call_time(staticmethod_id) == 1 if enable_fastreg else 2
    )  # directly called
    assert get_call_time(static_caller_id) == 1  # directly called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[staticmethod_id],
)
def test_class_staticmethod(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

    set_call_time(staticmethod_id, 0)

    tcid = next(gen2)

    hello = Hello()
    hello.staticmethod(10, 20)
    assert get_call_time(staticmethod_id) == 1  # directly called

    assert_test_case_files_exist(staticmethod_id, tcid)

    set_call_time(staticmethod_id, 0)

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == staticmethod_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(staticmethod_id) == 1  # directly called


@pytest.mark.parametrize("enable_fastreg", [True, False])
@make_test_autoreg(
    fcid_list=[hello_id, stub_id],
)
def test_class(enable_fastreg):
    gen1, gen2 = itertools.tee(gen(), 2)
    set_test_case_id_generator(gen1)

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

    args = ["--enable-fastreg"] if enable_fastreg else []
    test_results = artest.artest.main(args)

    assert len(test_results) == 1
    assert test_results[0].fcid == hello_id
    assert test_results[0].tcid == tcid
    assert test_results[0].status == StatusTestResult.SUCCESS

    assert get_call_time(hello_id) == 1  # directly called
    assert get_call_time(stub_id) == 0  # stubbed by artest, should not be called
