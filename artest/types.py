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
