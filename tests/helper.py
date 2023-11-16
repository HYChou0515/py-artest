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
import shutil
from contextlib import contextmanager
from functools import wraps


def pop_all_from_list(lst):
    """Clears all elements from a list.

    Args:
        lst (list): The list to be cleared.
    """
    while lst:
        lst.pop()


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
    shutil.rmtree(f"./.artest/{fcid}/{tcid}")


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
