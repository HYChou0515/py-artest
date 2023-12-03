"""This module provides config for checking whether two objects are equal.

Functions and Classes:
    - set_is_equal(func): Sets the function for comparing two objects.
    - get_is_equal(): Gets the function for comparing two objects.

"""


def _default_is_equal(actual, expected):
    if isinstance(actual, Exception) and isinstance(expected, Exception):
        return str(actual) == str(expected) and type(actual) == type(expected)
    return actual == expected


_is_equal = _default_is_equal


def set_is_equal(func):
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
