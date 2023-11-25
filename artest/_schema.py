from dataclasses import dataclass
from typing import Literal, NamedTuple, Optional

FunctionOutput = NamedTuple(
    "FunctionOutput",
    [
        ("output_type", Literal["return", "raise"]),
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
