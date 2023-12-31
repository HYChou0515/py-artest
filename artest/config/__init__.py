"""Package Initialization for Serialization and Test Case Utilities.

This package provides functionalities for serialization and test case management.

Functions and Modules Available:
    - get_pickler(): Gets the pickler object for serialization.
    - set_pickler(): Sets the pickler object for serialization.
    - get_test_case_id_generator: Gets the test case ID generator function.
    - set_test_case_id_generator(): Sets the test case ID generator function.
    - get_on_pickle_dump_error(): Gets the action to take on specific pickling errors.
    - set_on_pickle_dump_error(): Sets the action to take on specific pickling errors.
    - get_assert_pickled_object_on_case_mode(): Gets the status of asserting pickled object on case mode.
    - set_assert_pickled_object_on_case_mode(): Sets whether to assert pickled object on case mode.
    - get_function_root_path(): Gets the root path of the function.
    - set_function_root_path(): Sets the root path of the function.
    - get_is_equal(): Gets the function for comparing two objects.
    - set_is_equal(): Sets the function for comparing two objects.
    - get_stringify_obj(): Gets the function for converting an object to a string.
    - set_stringify_obj(): Sets the function for converting an object to a string.
    - get_message_formatter(): Gets the function for formatting the message.
    - set_message_formatter(): Sets the function for formatting the message.
    - get_printer(): Gets the function for printing the message.
    - set_printer(): Sets the function for printing the message.
    - get_artest_root(): Gets the root path of artest.
    - set_artest_root(): Sets the root path of artest.
    - get_on_func_id_duplicate(): Gets the action when a duplicate func_id is found.
    - set_on_func_id_duplicate(): Sets the action when a duplicate func_id is found.
    - get_test_case_quota(): Gets the test case quota.
    - set_test_case_quota(): Sets the test case quota.
    - reset_all_test_case_quota(): Resets all test case quota.

"""

__all__ = [
    "get_pickler",
    "set_pickler",
    "get_test_case_id_generator",
    "set_test_case_id_generator",
    "get_on_pickle_dump_error",
    "set_on_pickle_dump_error",
    "get_assert_pickled_object_on_case_mode",
    "set_assert_pickled_object_on_case_mode",
    "set_function_root_path",
    "get_function_root_path",
    "set_is_equal",
    "get_is_equal",
    "set_stringify_obj",
    "get_stringify_obj",
    "set_message_formatter",
    "get_message_formatter",
    "set_printer",
    "get_printer",
    "MessageRecord",
    "set_artest_root",
    "get_artest_root",
    "get_on_func_id_duplicate",
    "set_on_func_id_duplicate",
    "get_test_case_quota",
    "set_test_case_quota",
    "reset_all_test_case_quota",
]

from ..types import MessageRecord
from ._func_repo import get_on_func_id_duplicate, set_on_func_id_duplicate
from ._id_generator import get_test_case_id_generator, set_test_case_id_generator
from ._match_result import get_is_equal, set_is_equal
from ._paths import (
    get_artest_root,
    get_function_root_path,
    set_artest_root,
    set_function_root_path,
)
from ._pickler import (
    get_assert_pickled_object_on_case_mode,
    get_on_pickle_dump_error,
    get_pickler,
    set_assert_pickled_object_on_case_mode,
    set_on_pickle_dump_error,
    set_pickler,
)
from ._printer import (
    get_message_formatter,
    get_printer,
    get_stringify_obj,
    set_message_formatter,
    set_printer,
    set_stringify_obj,
)
from ._tc_quota import (
    get_test_case_quota,
    reset_all_test_case_quota,
    set_test_case_quota,
)
