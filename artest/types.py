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
from typing import NamedTuple, Optional


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
TestResult = NamedTuple(
    "TestResult",
    [
        ("is_success", bool),
        ("fcid", str),
        ("tcid", str),
        ("message", str),
    ],
)


@dataclass
class MessageRecord:
    """Represents a message record."""

    is_success: bool
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
    REPLACE = "replace"
    IGNORE = "ignore"


class ArtestMode(str, Enum):
    """Artest Modes."""

    DISABLE = "disable"
    CASE = "case"
    TEST = "test"
    USE_ENV = "use_env"
