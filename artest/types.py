"""Module for types definition.

This module provides functionality for types definition.

Classes:
    - FunctionOutput: Represents the output of a function.
    - TestResult: Represents the result of a test.
    - MessageRecord: Represents a message record.

Enums:
    - OnPickleDumpErrorAction: Actions enums on pickle dump error.
    - OnFuncIdDuplicateAction: Actions enums on function id duplicate.
    - ArtestMode: Artest Modes.
    - FunctionOutputType: Function output types.


"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal, NamedTuple, Optional, Union


class FunctionOutputType(str, Enum):
    """Function output types."""

    RETURN = "return"
    RAISE = "raise"


FunctionOutput = NamedTuple(
    "FunctionOutput",
    [
        ("output_type", FunctionOutputType),
        ("output", object),
    ],
)


class StatusTestResult(str, Enum):
    """Test result status."""

    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    REFRESH = "REFRESH"
    ERROR = "ERROR"


TestResult = NamedTuple(
    "TestResult",
    [
        ("status", StatusTestResult),
        ("fcid", str),
        ("tcid", str),
        ("message", str),
    ],
)


@dataclass
class MessageRecord:
    """Represents a message record."""

    result_status: StatusTestResult
    fcid: str
    tcid: str
    message: Optional[str] = None
    inputs: Optional[object] = None
    expected_outputs: Optional[FunctionOutput] = None
    actual_outputs: Optional[FunctionOutput] = None
    func: Optional[object] = None


class OnPickleDumpErrorAction(str, Enum):
    """Actions enums on pickle dump error."""

    IGNORE = "ignore"
    RAISE = "raise"
    WARNING = "warning"


class OnFuncIdDuplicateAction(str, Enum):
    """Actions enums on function id duplicate."""

    RAISE = "raise"
    IGNORE = "ignore"


class ArtestMode(str, Enum):
    """Artest Modes."""

    DISABLE = "disable"
    CASE = "case"
    TEST = "test"
    USE_ENV = "use_env"


@dataclass
class ConfigTestCaseQuota:
    """Config for test case quota.

    Attributes:
        max_count (Optional[Union[int, Literal['inf']]]): The max count of test cases.
    """

    max_count: Optional[Union[int, Literal["inf"]]] = None


@dataclass
class ArtestConfig:
    """Artest config.

    Attributes:
        mode (Literal['refresh', 'test']): The artest mode.
        include_function (Optional[list[str]]): The list of function ids to be included.
        include_test_case (Optional[list[str]]): The list of test case ids to be included.
        exclude_function (Optional[list[str]]): The list of function ids to be excluded.
        exclude_test_case (Optional[list[str]]): The list of test case ids to be excluded.
    """

    mode: Literal["refresh", "test"] = "test"
    include_function: Union[None, list[str]] = None
    include_test_case: Union[None, list[str]] = None
    exclude_function: Union[None, list[str]] = None
    exclude_test_case: Union[None, list[str]] = None


@dataclass
class MetadataTestCase:
    """Metadata for a test case.

    Attributes:
        version (str): The version of the test case.
        test_case_created_time (str): The created time of the test case.
        func_id (str): The function id.
        test_case_id (str): The test case id.
        hash_hex (str): The hash of the test case.
        bytes_size (int): The size of the test case in bytes.
    """

    version: str
    test_case_created_time: str
    func_id: str
    test_case_id: str
    hash_hex: str
    bytes_size: int


@dataclass
class Metadata:
    """Contains metadata for a collection of test cases.

    Attributes:
        test_cases (list[MetadataTestCase]): A list of MetadataTestCase objects representing individual test cases.
    """

    test_cases: list[MetadataTestCase] = None

    def __post_init__(self):
        """Initializes Metadata object by converting provided test case data into MetadataTestCase objects.

        This method is particularly useful when loading metadata from a JSON file.
        """
        if isinstance(self.test_cases, (list, tuple)):
            self.test_cases = [MetadataTestCase(**tc) for tc in self.test_cases]
        if self.test_cases is None:
            self.test_cases = []
