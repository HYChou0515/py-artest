"""artest: Automated Regression Testing Framework.

artest is a Python package designed for automated regression testing, providing decorators and utilities for efficient test case management.

Modules:
    - artest: Contains decorators for automatic regression and stubbing.

Public Objects:
    - autoreg: Decorator for creating regression tests during runtime.
    - autostub: Decorator for automatic stubbing during test execution.
    - search_meta: Search for metadata of test cases.

Version: 0.3.0
"""

__all__ = ["autoreg", "autostub", "search_meta"]
__version__ = "0.3.0"

from .artest import autoreg, autostub, search_meta
