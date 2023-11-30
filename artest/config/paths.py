"""This module provides functions to find the root path of the function.

Functions:
    - set_function_root_path(root_path): Sets the root path of the function.
    - get_function_root_path(): Gets the root path of the function.
"""


import os.path

_function_root_path = None
_artest_root = None


def set_artest_root(root_path):
    """Sets the root path of artest.

    Args:
        root_path: The root path to be set.
    """
    global _artest_root
    _artest_root = os.path.abspath(root_path)


def get_artest_root():
    """Gets the root path of artest.

    Returns:
        str: The root path of artest.
    """
    global _artest_root
    if _artest_root is None:
        return f"{os.getcwd()}/.artest"
    return _artest_root


def set_function_root_path(root_path):
    """Sets the root path of the function.

    Args:
        root_path: The root path to be set.
    """
    global _function_root_path
    _function_root_path = os.path.abspath(root_path)


def get_function_root_path():
    """Gets the root path of the function.

    Returns:
        str: The root path of the function.
    """
    global _function_root_path
    if _function_root_path is None:
        return os.getcwd()
    return _function_root_path
