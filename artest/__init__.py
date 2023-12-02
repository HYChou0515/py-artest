"""artest: Automated Regression Testing Framework.

artest is a Python package designed for automated regression testing, providing decorators and utilities for efficient test case management.

Modules:
    - artest: Contains decorators for automatic regression and stubing.

Public Objects:
    - autoreg: Decorator for creating regression tests during runtime.
    - autostub: Decorator for automatic stubing during test execution.

Version: 0.2.3
"""

__all__ = ["autoreg", "autostub"]
__version__ = "0.2.3"

from .artest import autoreg, autostub
