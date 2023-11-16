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
]

from .id_generator import set_test_case_id_generator, test_case_id_generator
from .pickler import (
    get_assert_pickled_object_on_case_mode,
    get_on_pickle_dump_error,
    get_pickler,
    set_assert_pickled_object_on_case_mode,
    set_on_pickle_dump_error,
    set_pickler,
)
