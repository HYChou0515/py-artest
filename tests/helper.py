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

import os
import pickle
import shutil
from contextlib import contextmanager
from functools import wraps


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


def get_call_time(id):
    try:
        with open(f"./{id}.calltime.pkl", "rb") as f:
            call_time = pickle.load(f)
    except Exception:
        call_time = 0
    return call_time


def set_call_time(id, call_time):
    with open(f"./{id}.calltime.pkl", "wb") as f:
        pickle.dump(call_time, f)


def assert_test_case_files_exist(fcid, tcid):
    """Asserts the existence of test case files.

    Args:
        fcid (str): The directory for the test case.
        tcid (str): The test case ID.
    """
    assert os.path.exists(f"./.artest/{fcid}/{tcid}/inputs")
    assert os.path.exists(f"./.artest/{fcid}/{tcid}/outputs")
    assert os.path.exists(f"./.artest/{fcid}/{tcid}/func")


def cleanup_test_case_files(fcid, tcid):
    """Cleans up test case files.

    Args:
        fcid (str): The directory for the test case.
        tcid (str): The test case ID.
    """
    shutil.rmtree(f"./.artest/{fcid}/{tcid}", ignore_errors=True)


def make_cleanup_test_case_files(fcid, tcid):
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
                cleanup_test_case_files(fcid, tcid)

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


def make_test_autoreg():
    """Decorator factory to set the test mode for automatic regression tests.

    Returns:
        function: Decorator function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with environ("ARTEST_MODE", "case"):
                func(*args, **kwargs)

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
