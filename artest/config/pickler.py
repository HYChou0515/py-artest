from collections import OrderedDict
from typing import Literal, NamedTuple, Union

_pickler = None


class _PickleErrorMatcher(NamedTuple):
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
    global _pickler
    _pickler = pkl


def get_pickler():
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
    global _on_pickle_dump_error
    for matcher, action in _on_pickle_dump_error.items():
        if isinstance(error, matcher.exception):
            if matcher.message is None or matcher.message in str(error):
                return action
    return "warning"


def set_assert_pickled_object_on_case_mode(assert_pickled_object_on_case_mode):
    global _assert_pickled_object_on_case_mode
    _assert_pickled_object_on_case_mode = assert_pickled_object_on_case_mode


def get_assert_pickled_object_on_case_mode():
    global _assert_pickled_object_on_case_mode
    return _assert_pickled_object_on_case_mode
