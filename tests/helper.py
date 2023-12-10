"""Utilities for Test Case Handling and Environment Control.

This module provides various utilities for managing test case files, environment settings,
and decorators for test automation.

Functions and Classes:
    - pop_all_from_list(lst): Clears all elements from a list.
    - assert_test_case_files_exist(fcid, tcid): Asserts the existence of test case files.
    - cleanup_test_case_files(fcid, tcid): Cleans up test case files.
    - environ(target, value): Context manager to temporarily set environment variables.
    - make_test_autoreg(): Decorator factory to set the test mode for automatic regression tests.
"""
import importlib
import os
import pickle
import shutil
import sys
from contextlib import contextmanager
from functools import wraps

import artest
from artest.artest import _meta_handler
from artest.config import (
    reset_all_test_case_quota,
    set_is_equal,
    set_message_formatter,
    set_on_func_id_duplicate,
    set_printer,
    set_stringify_obj,
    set_test_case_id_generator,
)
from artest.types import ArtestMode


def get_test_root_path():
    """Gets the root path of the function.

    Returns:
        str: The root path of the function.
    """
    return os.path.abspath(os.path.dirname(__file__))


def pop_all_from_list(lst):
    """Clears all elements from a list.

    Args:
        lst (list): The list to be cleared.
    """
    while lst:
        lst.pop()


def call_time_path(id):
    return f"./.test-only.{id}.calltime.pkl"


def get_call_time(id):
    try:
        with open(call_time_path(id), "rb") as f:
            call_time = pickle.load(f)
    except Exception:
        call_time = 0
    return call_time


def set_call_time(id, call_time):
    with open(call_time_path(id), "wb") as f:
        pickle.dump(call_time, f)


def assert_test_case_files_exist(fcid, tcid, *, assert_not_exist=False):
    """Asserts the existence of test case files.

    Args:
        fcid (str): The function ID.
        tcid (str): The test case ID.
        assert_not_exist (bool, optional): Whether to assert that the files do not exist.
    """
    assert assert_not_exist ^ os.path.exists(f"./.artest/{fcid}/{tcid}/inputs")
    assert assert_not_exist ^ os.path.exists(f"./.artest/{fcid}/{tcid}/outputs")
    assert assert_not_exist ^ os.path.exists(f"./.artest/{fcid}/{tcid}/func")


def assert_metadata_files_exist(fcid, tcid):
    """Asserts the existence of metadata files.

    Args:
        fcid (str): The function ID.
        tcid (str): The test case ID.
    """
    assert os.path.exists("./.artest/meta.json")
    from artest import search_meta

    assert search_meta(fcid, tcid, on_missing="none") is not None


def cleanup_test_case_files(fcid):
    """Cleans up test case files.

    Args:
        fcid (str): The function ID.
    """
    shutil.rmtree(f"./.artest/{fcid}", ignore_errors=True)


def make_cleanup_test_case_files(fcid):
    """Decorator factory to clean up test case files.

    Returns:
        function: Decorator function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            finally:
                cleanup_test_case_files(fcid)

        return wrapper

    return decorator


def make_cleanup_file(filepath):
    """Decorator factory to clean up a file.

    Returns:
        function: Decorator function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)

        return wrapper

    return decorator


@contextmanager
def environ(target, value):
    """Context manager to temporarily set environment variables.

    Args:
        target (str): The environment variable to set.
        value (str): The value to assign to the environment variable.
    """
    original = os.environ.get(target)
    os.environ[target] = value
    try:
        yield
    finally:
        if original is None:
            del os.environ[target]
        else:
            os.environ[target] = original


def make_test_autoreg(
    *,
    fcid_list=None,
    more_files_to_clean=None,
    more_callbacks=None,
    remove_modules=None,
):
    """Decorator factory to set the test mode for automatic regression tests.

    Returns:
        function: Decorator function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with environ("ARTEST_MODE", ArtestMode.CASE.value):
                for mod in remove_modules or []:
                    # [k for k in sys.modules.keys() if k.endswith(f".hello")]
                    del_modules = [
                        k for k in sys.modules.keys() if k.endswith(f".{mod}")
                    ]
                    for dm in del_modules:
                        del sys.modules[dm]
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    raise e
                finally:
                    for mod in remove_modules or []:
                        del_modules = [
                            k for k in sys.modules.keys() if k.endswith(f".{mod}")
                        ]
                        for dm in del_modules:
                            del sys.modules[dm]
                    for fcid in fcid_list or []:
                        cleanup_test_case_files(fcid)
                        if os.path.exists(call_time_path(fcid)):
                            os.remove(call_time_path(fcid))

                    for filepath in more_files_to_clean or []:
                        if os.path.exists(filepath):
                            os.remove(filepath)

                    for callback in more_callbacks or []:
                        try:
                            callback()
                        finally:
                            pass
                    set_test_case_id_generator()
                    set_on_func_id_duplicate()
                    set_is_equal()
                    set_message_formatter()
                    set_printer()
                    set_stringify_obj()
                    reset_all_test_case_quota()
                    _meta_handler.remove()
                    importlib.reload(artest.config)
                    importlib.reload(artest.artest)

        return wrapper

    return decorator


def make_callback(callback):
    """Decorator factory to set the test mode for automatic regression tests.

    Returns:
        function: Decorator function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            finally:
                callback()

        return wrapper

    return decorator
