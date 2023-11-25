"""Package Initialization for Serialization and Test Case Utilities.

This package provides functionalities for serialization and test case management.

Functions and Modules Available:
    - get_pickler(): Gets the pickler object for serialization.
    - set_pickler(): Sets the pickler object for serialization.
    - test_case_id_generator: Generator function for test case IDs.
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
    - MessageRecord: Represents a message record.

Submodules:
    - id_generator: Module for test case ID generation utilities.
    - pickler: Module for pickling and error handling utilities.
"""

__all__ = [
    "get_pickler",
    "set_pickler",
    "test_case_id_generator",
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
]

from .._schema import MessageRecord
from .find_functions import get_function_root_path, set_function_root_path
from .id_generator import set_test_case_id_generator, test_case_id_generator
from .match_result import get_is_equal, set_is_equal
from .pickler import (
    get_assert_pickled_object_on_case_mode,
    get_on_pickle_dump_error,
    get_pickler,
    set_assert_pickled_object_on_case_mode,
    set_on_pickle_dump_error,
    set_pickler,
)
from .printer import (
    get_message_formatter,
    get_printer,
    get_stringify_obj,
    set_message_formatter,
    set_printer,
    set_stringify_obj,
)
