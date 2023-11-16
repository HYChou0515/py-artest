"""Test Case ID Management Module.

This module provides functionality for managing unique test case IDs within the artest framework.
It includes a class `TestCaseIdGenerator` and functions for generating and setting test case IDs.

Classes:
    - TestCaseIdGenerator: Manages the generation of unique test case IDs.

Functions:
    - default_test_case_id_generator(): Generates unique IDs for test cases.
    - set_test_case_id_generator(gen=None): Sets a custom test case ID generator.

Public Objects:
    - test_case_id_generator: Instance of `TestCaseIdGenerator` for generating test case IDs.

Usage:
    from artest.id_generator import test_case_id_generator

    next_id = next(test_case_id_generator)  # Get the next unique test case ID
    test_case_id_generator.set_test_case_id_generator(my_custom_generator)  # Set a custom ID generator

"""

from uuid import uuid4


class TestCaseIdGenerator:
    """Generates unique test case IDs.

    This class manages the generation of unique test case IDs used within the artest framework.
    It implements the iterable protocol to generate IDs on demand.

    Usage:
        generator = TestCaseIdGenerator()
        next_id = next(generator)  # Get the next unique test case ID

    """

    def __init__(self):
        """Initializes the TestCaseIdGenerator.

        This method initializes the TestCaseIdGenerator class.
        It sets up the internal generator used for generating test case IDs when iterated.

        Usage:
            generator = TestCaseIdGenerator()  # Initialize the test case ID generator

        """
        self._gen = None

    def __next__(self):
        """Generates the next unique test case ID."""
        if self._gen is None:
            self._gen = _test_case_id_generator
        return next(self._gen)

    def __iter__(self):
        """Allows the object to be an iterable."""
        return self


def default_test_case_id_generator():
    """Generates unique IDs for test cases.

    This function serves as the default generator for unique test case IDs within artest.
    It generates IDs using UUID4 and returns them as strings.

    Returns:
        str: A unique test case ID.

    Usage:
        id = default_test_case_id_generator()  # Get a unique test case ID

    """
    while True:
        yield f"tc-{str(uuid4())[:8]}"


_test_case_id_generator = default_test_case_id_generator()


def set_test_case_id_generator(gen=None):
    """Sets the test case ID generator function.

    This function allows setting a custom test case ID generator. If not provided,
    it reverts to the default ID generator.

    Args:
        gen (callable, optional): Custom test case ID generator function.

    Usage:
        set_test_case_id_generator(my_custom_generator)  # Set a custom ID generator

    """
    global _test_case_id_generator
    _test_case_id_generator = gen


test_case_id_generator = TestCaseIdGenerator()
