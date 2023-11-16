"""ARTEST: Automatic Regression Testing.

This module provides decorators and utilities for automatic regression testing.
"""

import hashlib
import inspect
import os
import warnings
from functools import wraps
from glob import glob

from artest.config import (
    get_assert_pickled_object_on_case_mode,
    get_on_pickle_dump_error,
    get_pickler,
    test_case_id_generator,
)

ARTEST_ROOT = "./.artest"


def get_artest_mode():
    """Get the current artest mode.

    Returns:
        str: The current artest mode.
    """
    return os.environ.get("ARTEST_MODE", "disable")


class TestCaseSerializer:
    """Handles serialization and deserialization of test case objects."""

    @staticmethod
    def dump(obj, fp):
        """Serialize an object to a file-like object.

        Args:
            obj: The object to be serialized.
            fp: File-like object to write serialized data.
        """
        pickler = get_pickler()
        try:
            pickler.dump(obj, fp)
        except Exception as e:
            action = get_on_pickle_dump_error(e)
            if action == "ignore":
                return
            if action == "raise":
                raise e
            if action == "warning":
                warnings.warn(str(e))

    @staticmethod
    def dumps(obj):
        """Serialize an object to a bytes object.

        Args:
            obj: The object to be serialized.

        Returns:
            bytes: Serialized object as bytes.
        """
        return get_pickler().dumps(obj)

    @staticmethod
    def load(fp):
        """Deserialize an object from a file-like object.

        Args:
            fp: File-like object to read serialized data.

        Returns:
            Deserialized object.
        """
        return get_pickler().load(fp)

    def save(self, obj, path):
        """Save the serialized object to a file.

        Args:
            obj: The object to be serialized.
            path: Path to save the serialized object.
        """
        dirpath = os.path.dirname(path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(path, "wb") as f:
            self.dump(obj, f)

    def save_inputs(self, inputs: dict[str], path):
        """Save the input dictionary to a file.

        Args:
            inputs: Dictionary containing input data.
            path: Path to save the input dictionary.
        """
        assert isinstance(inputs, dict)
        return self.save(inputs, path)

    def save_func(self, func, path):
        """Save the function to a file.

        Args:
            func: The function to be saved.
            path: Path to save the function.
        """
        return self.save(func, path)

    def read(self, path):
        """Read a serialized object from a file.

        Args:
            path: Path to the serialized object file.

        Returns:
            Deserialized object.
        """
        with open(path, "rb") as f:
            return self.load(f)

    def read_inputs(self, path):
        """Read the input dictionary from a file.

        Args:
            path: Path to the input dictionary file.

        Returns:
            dict: Input dictionary.
        """
        return self.read(path)

    def read_func(self, path):
        """Read a function from a file.

        Args:
            path: Path to the function file.

        Returns:
            Function object.
        """
        return self.read(path)

    def calc_hash(self, obj):
        """Calculate the SHA256 hash of a serialized object.

        Args:
            obj: The object to calculate the hash for.

        Returns:
            str: SHA256 hash string.
        """
        return hashlib.sha256(self.dumps(obj)).hexdigest()[10:20]


def _build_path(fcid, tcid, basename):
    return os.path.join(ARTEST_ROOT, fcid, tcid, basename)


AUTOREG_REGISTERED = set()
AUTOMOCK_REGISTERED = set()
test_stack = []


def autoreg(func_id: str):
    """Auto Regression Test Decorator.

    This decorator facilitates the automatic creation and management of regression tests during runtime.
    Created test cases are stored in a directory for future testing.

    Algorithm:
    Under 'Case Mode':
    1. Generate a test case ID and push it to the test stack.
    2. Execute the function:
       2.1. If a sub-function is decorated with autoreg, run it recursively.
       2.2. If the sub-function is decorated with automock:
            - Calculate the input hash.
            - Execute the function.
            - For each caller-fcid,tcid in the stack:
                Save output under /caller-fcid/tcid/mock/fcid.order.inputhash.output.
    3. Save the serialized input and output under /fcid/tcid/input,output.
    4. Pop the test stack.

    Under 'Test Mode':
    1. Given fcid and tcid inferred from the directory structure.
    2. Load the input and output from /fcid/tcid/input,output.
    3. Execute the function:
       3.1. If a sub-function is decorated with autoreg, run the function normally.
       3.2. If the sub-function is decorated with automock:
            - Calculate the input hash.
            - Load the output from /caller_fcid/tcid/mock/fcid.order.inputhash.output.
    4. Compare the output with the loaded one.

    Args:
        func_id (str): The identifier for the function.

    Returns:
        function: Decorated function.

    Raises:
        ValueError: If the provided function ID is already registered in autoreg.
    """
    func_id = str(func_id)
    if func_id in AUTOREG_REGISTERED:
        raise ValueError(f"Function {func_id} is already registered in autoreg.")
    AUTOREG_REGISTERED.add(func_id)

    serializer = TestCaseSerializer()

    def _autoreg(func):
        def disable_mode(*args, **kwargs):
            return func(*args, **kwargs)

        def case_mode(*args, **kwargs):
            tcid = next(test_case_id_generator)
            test_stack.append((func_id, tcid))
            f_inputs = _build_path(func_id, tcid, "inputs")
            f_outputs = _build_path(func_id, tcid, "outputs")
            f_func = _build_path(func_id, tcid, "func")
            arguments = inspect.getcallargs(func, *args, **kwargs)
            serializer.save_inputs(arguments, f_inputs)
            serializer.save_func(func, f_func)
            ret = func(*args, **kwargs)
            serializer.save(ret, f_outputs)
            if get_assert_pickled_object_on_case_mode():
                ret_saved = serializer.read(f_outputs)
                assert serializer.dumps(ret) == serializer.dumps(ret_saved)
            test_stack.pop()
            return ret

        def test_mode(*args, **kwargs):
            return func(*args, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs):
            artest_mode = get_artest_mode()
            if artest_mode == "disable":
                return disable_mode(*args, **kwargs)
            elif artest_mode == "case":
                return case_mode(*args, **kwargs)
            elif artest_mode == "test":
                return test_mode(*args, **kwargs)
            raise ValueError(f"Unknown artest mode {artest_mode}")

        return wrapper

    return _autoreg


def automock(func_id: str):
    """Automock Decorator.

    This decorator is utilized to generate and manage mock data for functions during testing.
    The decorator orchestrates the handling of mock data creation and retrieval based on specified modes.

    Args:
        func_id (str): The identifier for the function.

    Returns:
        function: Decorated function.

    Raises:
        ValueError: If the provided function ID is already registered in automock.
    """
    func_id = str(func_id)
    if func_id in AUTOMOCK_REGISTERED:
        raise ValueError(f"Function {func_id} is already registered in automock.")
    AUTOMOCK_REGISTERED.add(func_id)

    serializer = TestCaseSerializer()
    counts = {}

    def _automock(func):
        """Internal function within the automock decorator."""

        def disable_mode(*args, **kwargs):
            return func(*args, **kwargs)

        def _basename(func_id, call_count, input_hash):
            """Generates the basename for mock output files."""
            return os.path.join("mock", f"{func_id}.{call_count}.{input_hash}.output")

        def case_mode(*args, **kwargs):
            """Handles the functionality under 'Case Mode'."""
            arguments = inspect.getcallargs(func, *args, **kwargs)
            input_hash = serializer.calc_hash(arguments)
            result = func(*args, **kwargs)
            for caller_fcid, tcid in test_stack:
                call_count = counts.get((caller_fcid, tcid), 0)
                counts[(caller_fcid, tcid)] = call_count + 1
                serializer.save(
                    result,
                    _build_path(
                        caller_fcid,
                        tcid,
                        _basename(func_id, call_count, input_hash),
                    ),
                )
            return result

        def test_mode(*args, **kwargs):
            """Handles the functionality under 'Test Mode'."""
            caller_fcid = os.environ["__ARTEST_FCID"]
            tcid = os.environ["__ARTEST_TCID"]

            call_count = counts.get((caller_fcid, tcid), 0)
            counts[(caller_fcid, tcid)] = call_count + 1

            arguments = inspect.getcallargs(func, *args, **kwargs)
            input_hash = serializer.calc_hash(arguments)
            path = _build_path(
                caller_fcid,
                tcid,
                _basename(func_id, call_count, input_hash),
            )
            if not os.path.exists(path):
                raise ValueError(f"Mock file missing: {path}")
            result = serializer.read(path)
            return result

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper function determining the behavior based on artest_mode."""
            artest_mode = get_artest_mode()
            if artest_mode == "disable":
                return disable_mode(*args, **kwargs)
            elif artest_mode == "case":
                return case_mode(*args, **kwargs)
            elif artest_mode == "test":
                return test_mode(*args, **kwargs)
            raise ValueError(f"Unknown artest mode {artest_mode}")

        return wrapper

    return _automock


def _info(s="", *args, **kwargs):
    print(f"ARTEST: {s}", *args, **kwargs)


def main():
    """Execute Automated Regression Testing.

    This function orchestrates the automated regression testing process by emulating the testing environment
    and comparing expected outputs with the actual function outputs saved in serialized files.
    The function reads test cases from a predefined directory structure, executes the associated function,
    and compares the outputs.

    It cycles through each test case directory, retrieves inputs, expected outputs, and the function,
    then executes the function using the inputs and validates the output against the saved expected output.

    Note:
        The function relies on the TestCaseSerializer for serialization and deserialization.

    Raises:
        ValueError: If the inputs, outputs, or func files are missing for a test case directory.
                    Or if an exception occurs during function execution.

    """
    serializer = TestCaseSerializer()
    orig_artest_mode = os.environ.get("ARTEST_MODE", None)
    os.environ["ARTEST_MODE"] = "test"

    for path in glob(os.path.join(ARTEST_ROOT, "*", "*")):
        fcid, tcid = path.split(os.path.sep)[-2:]

        def info_test_result(is_success, message=""):
            s = []
            if is_success:
                s.append(f"{'SUCCESS':10s}")
            else:
                s.append(f"{'FAIL':10s}")
            s.append(f"fc={fcid}")
            s.append(f"tc={tcid}")
            if message:
                s.append(f"msg={message}")
            _info(" ".join(s))

        os.environ["__ARTEST_FCID"] = fcid
        os.environ["__ARTEST_TCID"] = tcid
        f_inputs = _build_path(fcid, tcid, "inputs")
        f_outputs = _build_path(fcid, tcid, "outputs")
        f_func = _build_path(fcid, tcid, "func")
        if os.path.exists(f_inputs):
            inputs = serializer.read_inputs(f_inputs)
        else:
            info_test_result(False, f"Inputs file {f_inputs} not found.")
            continue
        if os.path.exists(f_outputs):
            outputs = serializer.read(f_outputs)
        else:
            info_test_result(False, f"Outputs file {f_outputs} not found.")
            continue
        if os.path.exists(f_func):
            func = serializer.read_func(f_func)
        else:
            info_test_result(False, f"Func file {f_func} not found.")
            continue
        try:
            ret = func(**inputs)
        except Exception as e:
            info_test_result(False, f"Exception {e} raised.")
            continue
        if ret != outputs:
            info_test_result(False, "Outputs not matched.")
            continue
        info_test_result(True)

    del os.environ["__ARTEST_FCID"]
    del os.environ["__ARTEST_TCID"]
    del os.environ["ARTEST_MODE"]
    if orig_artest_mode is not None:
        os.environ["ARTEST_MODE"] = orig_artest_mode


if __name__ == "__main__":
    main()
