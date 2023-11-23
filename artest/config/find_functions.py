"""This module provides functions to find the root path of the function.

Functions:
    - set_function_root_path(root_path): Sets the root path of the function.
    - get_function_root_path(): Gets the root path of the function.
"""


import os.path

_function_root_path = None


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
