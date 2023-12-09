"""This module provides config for checking whether two objects are equal.

Functions and Classes:
    - set_is_equal(func): Sets the function for comparing two objects.
    - get_is_equal(): Gets the function for comparing two objects.

"""
from artest.config._pickler import get_pickler


def _default_is_equal(actual, expected):
    try:
        if isinstance(actual, Exception) and isinstance(expected, Exception):
            return str(actual) == str(expected) and type(actual) == type(expected)
        if actual == expected:
            return True
        return get_pickler().dumps(actual) == get_pickler().dumps(expected)
    except Exception:
        return False


_is_equal = _default_is_equal


def set_is_equal(func=None):
    """Sets the function for comparing two objects.

    Args:
        func (function): The function for comparing two objects.
    """
    global _is_equal

    def _new_default_is_equal(actual, expected):
        eq = func(actual, expected)
        if eq is not None:
            return eq
        return _default_is_equal(actual, expected)

    if func is None:
        _is_equal = _default_is_equal
    else:
        _is_equal = _new_default_is_equal


def get_is_equal():
    """Gets the function for comparing two objects.

    Returns:
        function: The function for comparing two objects.
    """
    return _is_equal
