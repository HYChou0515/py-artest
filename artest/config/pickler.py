"""Module for Pickle Error Handling and Serialization Utilities.

This module provides functionality for managing pickling errors and serialization settings.

Functions:
    - set_pickler(pkl): Sets the pickler to be used for serialization.
    - get_pickler(): Gets the pickler object for serialization.
    - set_on_pickle_dump_error(exception, action, message=None): Sets the action to take on specific pickling errors.
    - get_on_pickle_dump_error(error): Gets the action to take on a specific pickling error.
    - set_assert_pickled_object_on_case_mode(assert_pickled_object_on_case_mode): Sets whether to assert pickled object on case mode.
    - get_assert_pickled_object_on_case_mode(): Gets the status of asserting pickled object on case mode.

Classes:
    - _PickleErrorMatcher: Matches a specific pickle error.
    - _PickleErrorAction: Literal["warning", "ignore", "raise"]: Represents actions on pickling errors.
"""

from collections import OrderedDict
from typing import Literal, NamedTuple, Union

_pickler = None


class _PickleErrorMatcher(NamedTuple):
    """Matches a specific pickle error."""

    exception: type
    message: Union[str, None]


_PickleErrorAction = Literal["warning", "ignore", "raise"]

_on_pickle_dump_error = OrderedDict(
    [
        (
            _PickleErrorMatcher(exception=TypeError, message="can't pickle"),
            "warning",
        )
    ]
)

_assert_pickled_object_on_case_mode = False


def set_pickler(pkl):
    """Sets the pickler to be used for serialization.

    Args:
        pkl: The pickler object to be set.
    """
    global _pickler
    _pickler = pkl


def get_pickler():
    """Gets the pickler object for serialization.

    Returns:
        Pickler object: The pickler object to be used for serialization.
    """
    global _pickler
    if _pickler is None:
        try:
            import dill

            _pickler = dill
        except ImportError:
            import pickle

            _pickler = pickle
    return _pickler


def set_on_pickle_dump_error(exception, action: _PickleErrorAction, message=None):
    """Sets the action to take on specific pickling errors.

    Args:
        exception: The exception type to be handled.
        action (Literal["warning", "ignore", "raise"]): The action to take on encountering the exception.
        message (str, optional): The specific message within the exception. Defaults to None.
    """
    global _on_pickle_dump_error
    if message is None:
        # remove all previous entries with the same exception
        # and add the new one
        keys = list(_on_pickle_dump_error.keys())
        for k in keys:
            if k.exception == exception:
                del _on_pickle_dump_error[k]
        _on_pickle_dump_error[_PickleErrorMatcher(exception, None)] = action
    else:
        # remove message=None entry if exists
        if (
            _on_pickle_dump_error.get(_PickleErrorMatcher(exception, None), None)
            is not None
        ):
            del _on_pickle_dump_error[_PickleErrorMatcher(exception, None)]
        # add the new one
        _on_pickle_dump_error[_PickleErrorMatcher(exception, message)] = action


def get_on_pickle_dump_error(error) -> _PickleErrorAction:
    """Gets the action to take on a specific pickling error.

    Args:
        error: The pickling error.

    Returns:
        Literal["warning", "ignore", "raise"]: The action to take on encountering the error.
    """
    global _on_pickle_dump_error
    for matcher, action in _on_pickle_dump_error.items():
        if isinstance(error, matcher.exception):
            if matcher.message is None or matcher.message in str(error):
                return action
    return "warning"


def set_assert_pickled_object_on_case_mode(assert_pickled_object_on_case_mode):
    """Sets whether to assert pickled object on case mode.

    Args:
        assert_pickled_object_on_case_mode: Whether to assert pickled object on case mode or not.
    """
    global _assert_pickled_object_on_case_mode
    _assert_pickled_object_on_case_mode = assert_pickled_object_on_case_mode


def get_assert_pickled_object_on_case_mode():
    """Gets the status of asserting pickled object on case mode.

    Returns:
        bool: Whether to assert pickled object on case mode or not.
    """
    global _assert_pickled_object_on_case_mode
    return _assert_pickled_object_on_case_mode
