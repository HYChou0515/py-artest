"""Test Case ID Management Module.

This module provides functionality for managing test case IDs.

Functions:
    - set_test_case_id_generator(gen=None): Sets the test case ID generator function.
    - get_test_case_id_generator(): Gets the test case ID generator function.

Classes:
    - _TestCaseIdGenerator: Generates unique test case IDs.

"""

from uuid import uuid4


class _TestCaseIdGenerator:
    """Generates unique test case IDs.

    This class manages the generation of unique test case IDs used within the artest framework.
    It implements the iterable protocol to generate IDs on demand.

    Usage:
        generator = _TestCaseIdGenerator()
        next_id = next(generator)  # Get the next unique test case ID

    """

    def __init__(self, gen):
        """Initializes the _TestCaseIdGenerator.

        This method initializes the _TestCaseIdGenerator class.
        It sets up the internal generator used for generating test case IDs when iterated.

        Usage:
            generator = _TestCaseIdGenerator()  # Initialize the test case ID generator

        """
        self._gen = gen

    def __next__(self):
        """Generates the next unique test case ID."""
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


_test_case_id_generator = _TestCaseIdGenerator(default_test_case_id_generator())


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

    if gen is None:
        gen = default_test_case_id_generator()
    _test_case_id_generator = _TestCaseIdGenerator(gen)


def get_test_case_id_generator():
    """Gets the test case ID generator function.

    This function returns the current test case ID generator function.

    Returns:
        callable: The current test case ID generator function.

    Usage:
        generator = get_test_case_id_generator()  # Get the current ID generator

    """
    return _test_case_id_generator
