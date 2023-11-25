"""artest: Automated Regression Testing Framework.

artest is a Python package designed for automated regression testing, providing decorators and utilities for efficient test case management.

Modules:
    - artest: Contains decorators for automatic regression and mocking.

Public Objects:
    - autoreg: Decorator for creating regression tests during runtime.
    - automock: Decorator for automatic mocking during test execution.

Version: 0.2.2
"""

__all__ = ["autoreg", "automock"]
__version__ = "0.2.2"

from .artest import automock, autoreg
