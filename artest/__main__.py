"""artest Automated Testing Execution.

This module serves as an entry point to execute the artest automated testing suite.
When executed as a script, it triggers the artest's main function from the 'artest' package.

It imports and calls the main function from the 'artest' package, which orchestrates
the automated regression testing process, comparing expected outputs with actual function outputs
saved in serialized files.

Usage:
    This file can be executed directly to initiate the artest automated regression testing.

Example:
    To run automated regression testing using artest:
        python -m artest

Dependencies:
    - artest package

Note:
    Ensure the artest package is properly installed before executing this script.

"""

import artest

if __name__ == "__main__":
    artest.artest.main()
