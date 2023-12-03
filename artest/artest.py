"""ARTEST: Automatic Regression Testing.

This module provides decorators and utilities for automatic regression testing.

Functions:
    autoreg: Auto Regression Test Decorator.
    autostub: Autostub Decorator.
    main: Execute Automated Regression Testing.

"""

import ast
import hashlib
import importlib
import inspect
import os
import sys
import warnings
from collections.abc import MutableMapping
from contextvars import ContextVar
from functools import wraps
from glob import glob
from typing import Optional

from artest.config import (
    get_artest_root,
    get_assert_pickled_object_on_case_mode,
    get_function_root_path,
    get_is_equal,
    get_on_pickle_dump_error,
    get_pickler,
    get_test_case_id_generator,
)
from artest.config.printer import get_message_formatter, get_printer
from artest.types import (
    ArtestMode,
    FunctionOutput,
    FunctionOutputType,
    MessageRecord,
    OnFuncIdDuplicateAction,
    OnPickleDumpErrorAction,
    TestResult,
)

_overload_on_duplicate_var = ContextVar("__ARTEST_ON_DUPLICATE__", default=None)
_fcid_var = ContextVar("__ARTEST_FCID__")
_tcid_var = ContextVar("__ARTEST_TCID__")
_artest_mode_var = ContextVar("__ARTEST_MODE__", default=ArtestMode.USE_ENV)


def _extract_autoreg_assigned_variable(node: ast.AST) -> Optional[str]:
    """Identifies and retrieves the assigned variable name from an autoreg function call within an assignment.

    This function examines an AST node representing an assignment operation.
    If the assignment is of a variable to a direct call to autoreg, it returns the assigned variable name.

    Specifically, it checks if the node represents an assignment in the form of `var = autoreg(func_id)(func)`.

    Examples returning the assigned variable name:
    - `var = autoreg(func_id)(func)`

    Counterexamples returning None:
    - `r = autoreg(func_id); var = r(func)`
    - `var.attr = autoreg(func_id)(func)`
    - `var1, var2 = autoreg(func1_id)(func1), autoreg(func1_id)(func2)`

    Regarding the AST structure:
    - The node type is `ast.Assign`.
    - The `node.value` is of type `ast.Call`.
    - The `node.value.func` is also of type `ast.Call`.
    - The `node.value.func.func` is of type `ast.Name`.
    - The `node.value.func.func.id` corresponds to `autoreg`.
    """
    if not isinstance(node, ast.Assign):
        # not an assignment
        return None

    if not (
        isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Call)
        and isinstance(node.value.func.func, ast.Name)
        and node.value.func.func.id == "autoreg"
    ):
        # the right hand side is not a in the form of `autoreg(func_id)(func)`
        return None

    node_target = node.targets
    if not (len(node_target) == 1):
        # the left hand side is not one item
        return None

    node_target = node_target[0]
    if not (isinstance(node_target, ast.Name)):
        # the left hand side is not a variable name
        return None

    return node_target.id


def get_artest_decorators(target, *, target_is_source=False):
    """Get the decorators for a function.

    Args:
        target (str): The function to get decorators for.
        target_is_source (bool): Whether the target is a source code string.

    Returns:
        dict: A dictionary mapping function names to a list of decorators.
    """
    if target_is_source:
        pass
    else:
        target = inspect.getsource(target)

    autoreg_funcs = []

    try:
        tree = ast.parse(target)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for n in node.decorator_list:
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                        if n.func.id == "autoreg":
                            if hasattr(node, "parent"):
                                autoreg_funcs.append((node.parent.name, node.name))
                            else:
                                autoreg_funcs.append((None, node.name))

            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        child.parent = node
            var_name = _extract_autoreg_assigned_variable(node)
            if var_name is not None:
                autoreg_funcs.append((None, var_name))

    except SyntaxError:
        pass
    return autoreg_funcs


class _FunctionIdRepository(MutableMapping):
    """Repository for function IDs."""

    def __init__(self):
        self.store = dict()

    def __getitem__(self, key):
        if key in self.store:
            return self.store[key]

        def find_func():
            root_path = get_function_root_path()
            for python_path in sys.path:
                python_path = os.path.abspath(python_path)
                if not (
                    python_path.startswith(root_path)
                    or root_path.startswith(python_path)
                ):
                    continue

                for fname in glob(f"{python_path}/**/*.py", recursive=True):
                    if not fname.startswith(root_path):
                        continue
                    with open(fname, "r") as f:
                        source = f.read()
                    artest_functions = get_artest_decorators(
                        source, target_is_source=True
                    )
                    if not artest_functions:
                        continue
                    overload_on_duplicate_reset_token = _overload_on_duplicate_var.set(
                        OnFuncIdDuplicateAction.IGNORE
                    )
                    relpath = os.path.relpath(fname, python_path)
                    mod = importlib.import_module(relpath.replace("/", ".")[:-3])
                    # reload module seems to be a must when
                    # we try to mimic file change.
                    mod = importlib.reload(mod)
                    _overload_on_duplicate_var.reset(overload_on_duplicate_reset_token)
                    for class_name, func_name in artest_functions:
                        if class_name is None:
                            func = getattr(mod, func_name, None)
                            if func is not None and func.__artest_func_id__ == key:
                                return func
                        else:
                            cls = getattr(mod, class_name, None)
                            if cls is not None:
                                func = getattr(cls, func_name, None)
                                if func is None:
                                    continue
                                elif inspect.isdatadescriptor(func):
                                    func = func.fget
                                    if func.__artest_func_id__ == key:
                                        return func
                                elif inspect.ismethod(func):
                                    if func.__func__.__artest_func_id__ == key:
                                        return func.__func__
                                else:
                                    if func.__artest_func_id__ == key:
                                        return func
            return None

        func = find_func()
        if func is not None:
            self.store[key] = func
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)


_func_id_repo = _FunctionIdRepository()


def _get_artest_mode():
    """Get the current artest mode.

    Returns:
        str: The current artest mode.
    """
    if (_mode := _artest_mode_var.get()) == ArtestMode.USE_ENV:
        env_artest_mode = os.environ.get("ARTEST_MODE", ArtestMode.DISABLE)
        return ArtestMode(env_artest_mode)
    return _mode


class _TestCaseSerializer:
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
            if action == OnPickleDumpErrorAction.IGNORE:
                return
            if action == OnPickleDumpErrorAction.RAISE:
                raise e
            if action == OnPickleDumpErrorAction.WARNING:
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

    def save_inputs(self, inputs: tuple[tuple, dict], path):
        """Save the input dictionary to a file.

        Args:
            inputs: tuple of args and kwargs.
            path: Path to save the input dictionary.
        """
        return self.save(inputs, path)

    def save_func(self, fcid_tcid, path):
        """Save the function to a file.

        Args:
            fcid_tcid: tuple of function ID and test case ID.
            path: Path to save the function.
        """
        return self.save(fcid_tcid, path)

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
        assert path.endswith("/func")
        _, tcid, fcid, *_ = path.split("/")[::-1]
        func = _func_id_repo[fcid]
        return func

    def calc_hash(self, obj):
        """Calculate a short hash of an object.

        This is used to generate a unique identifier an input.

        Args:
            obj: The object to calculate the hash for.

        Returns:
            str: the hash string.
        """
        return hashlib.sha256(self.dumps(obj)).hexdigest()[10:20]


_serializer = _TestCaseSerializer()


def _build_path(fcid, tcid, basename):
    return os.path.join(get_artest_root(), fcid, tcid, basename)


_AUTOREG_REGISTERED = set()
_AUTOSTUB_REGISTERED = set()
_test_stack = []


def _get_func_output(func, args, kwargs):
    try:
        ret = func(*args, **kwargs)
        outputs = FunctionOutput(FunctionOutputType.RETURN, ret)
    except Exception as e:
        outputs = FunctionOutput(FunctionOutputType.RAISE, e)
    return outputs


def _find_class(func):
    import sys

    cls = sys.modules.get(func.__module__)
    if cls is None:
        return None
    for name in func.__qualname__.split(".")[:-1]:
        cls = getattr(cls, name)
    if not inspect.isclass(cls):
        return None
    return cls


def _find_input_hash(func, args, kwargs):
    cls = _find_class(func)
    arguments = inspect.getcallargs(func, *args, **kwargs)
    if cls is not None:
        if "self" in arguments:
            del arguments["self"]
    input_hash = _serializer.calc_hash(arguments)
    return input_hash


def autoreg(
    func_id: str,
    *,
    on_duplicate: OnFuncIdDuplicateAction = OnFuncIdDuplicateAction.RAISE,
):
    """Auto Regression Test Decorator.

    This decorator facilitates the automatic creation and management of regression tests during runtime.
    Created test cases are stored in a directory for future testing.

    Algorithm:
    Under 'Case Mode':
    1. Generate a test case ID and push it to the test stack.
    2. Execute the function:
       2.1. If a sub-function is decorated with autoreg, run it recursively.
       2.2. If the sub-function is decorated with autostub:
            - Calculate the input hash.
            - Execute the function.
            - For each caller-fcid,tcid in the stack:
                Save output under /caller-fcid/tcid/stub/fcid.order.inputhash.output.
    3. Save the serialized input and output under /fcid/tcid/input,output.
    4. Pop the test stack.

    Under 'Test Mode':
    1. Given fcid and tcid inferred from the directory structure.
    2. Load the input and output from /fcid/tcid/input,output.
    3. Execute the function:
       3.1. If a sub-function is decorated with autoreg, run the function normally.
       3.2. If the sub-function is decorated with autostub:
            - Calculate the input hash.
            - Load the output from /caller_fcid/tcid/stub/fcid.order.inputhash.output.
    4. Compare the output with the loaded one.

    Args:
        func_id (str): The identifier for the function.

    Returns:
        function: Decorated function.

    Raises:
        ValueError: If the provided function ID is already registered in autoreg.
    """
    if _overload_on_duplicate_var.get() is not None:
        on_duplicate = _overload_on_duplicate_var.get()
    func_id = str(func_id)
    if func_id in _AUTOREG_REGISTERED:
        if on_duplicate == OnFuncIdDuplicateAction.RAISE:
            raise ValueError(f"Function {func_id} is already registered in autoreg.")
    else:
        _AUTOREG_REGISTERED.add(func_id)

    def _autoreg(func):
        func.__artest_func_id__ = func_id

        def disable_mode(*args, **kwargs):
            return func(*args, **kwargs)

        def case_mode(*args, **kwargs):
            tcid = next(get_test_case_id_generator())
            _test_stack.append((func_id, tcid))
            f_inputs = _build_path(func_id, tcid, "inputs")
            f_outputs = _build_path(func_id, tcid, "outputs")
            f_func = _build_path(func_id, tcid, "func")
            _serializer.save_inputs((args, kwargs), f_inputs)
            _serializer.save_func((func_id, tcid), f_func)

            output = _get_func_output(func, args, kwargs)
            _serializer.save(output, f_outputs)
            if get_assert_pickled_object_on_case_mode():
                output_saved = _serializer.read(f_outputs)
                assert _serializer.dumps(output) == _serializer.dumps(output_saved)
            _test_stack.pop()
            if output.output_type == FunctionOutputType.RAISE:
                raise output.output
            return output.output

        def test_mode(*args, **kwargs):
            return func(*args, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs):
            artest_mode = _get_artest_mode()
            if artest_mode == ArtestMode.DISABLE:
                return disable_mode(*args, **kwargs)
            elif artest_mode == ArtestMode.CASE:
                return case_mode(*args, **kwargs)
            elif artest_mode == ArtestMode.TEST:
                return test_mode(*args, **kwargs)
            raise ValueError(f"Unknown artest mode {artest_mode}")

        return wrapper

    return _autoreg


_stub_counter = {}


def autostub(
    func_id: str,
    *,
    on_duplicate: OnFuncIdDuplicateAction = OnFuncIdDuplicateAction.RAISE,
):
    """Autostub Decorator.

    This decorator is utilized to generate and manage stub data for functions during testing.
    The decorator orchestrates the handling of stub data creation and retrieval based on specified modes.

    Args:
        func_id (str): The identifier for the function.

    Returns:
        function: Decorated function.

    Raises:
        ValueError: If the provided function ID is already registered in autostub.
    """
    if _overload_on_duplicate_var.get() is not None:
        on_duplicate = _overload_on_duplicate_var.get()
    func_id = str(func_id)
    if func_id in _AUTOSTUB_REGISTERED:
        if on_duplicate == OnFuncIdDuplicateAction.RAISE:
            raise ValueError(f"Function {func_id} is already registered in autostub.")
    else:
        _AUTOSTUB_REGISTERED.add(func_id)

    def _autostub(func):
        """Internal function within the autostub decorator."""

        def disable_mode(*args, **kwargs):
            return func(*args, **kwargs)

        def _basename(func_id, call_count, input_hash):
            """Generates the basename for stub output files."""
            return os.path.join("stub", f"{func_id}.{call_count}.{input_hash}.output")

        def case_mode(*args, **kwargs):
            """Handles the functionality under 'Case Mode'."""
            input_hash = None
            if _test_stack:
                # Need to find input hash before running the function
                # Because mutable inputs can be different
                # before and after running the function
                input_hash = _find_input_hash(func, args, kwargs)
            _test_stack.append(None)
            output = _get_func_output(func, args, kwargs)
            _test_stack.pop()
            for stack_item in _test_stack[::-1]:  # start from latest caller
                if stack_item is None:
                    break
                caller_fcid, tcid = stack_item
                call_count = _stub_counter.get((func_id, caller_fcid, tcid), 0)
                _stub_counter[(func_id, caller_fcid, tcid)] = call_count + 1
                _serializer.save(
                    output,
                    _build_path(
                        caller_fcid,
                        tcid,
                        _basename(func_id, call_count, input_hash),
                    ),
                )
            if output.output_type == FunctionOutputType.RAISE:
                raise output.output
            return output.output

        def test_mode(*args, **kwargs):
            """Handles the functionality under 'Test Mode'."""
            caller_fcid = _fcid_var.get()
            tcid = _tcid_var.get()

            call_count = _stub_counter.get((func_id, caller_fcid, tcid), 0)
            _stub_counter[(func_id, caller_fcid, tcid)] = call_count + 1

            input_hash = _find_input_hash(func, args, kwargs)
            path = _build_path(
                caller_fcid,
                tcid,
                _basename(func_id, call_count, input_hash),
            )
            if not os.path.exists(path):
                raise ValueError(f"Stub file missing: {path}")
            output: FunctionOutput = _serializer.read(path)
            if output.output_type == FunctionOutputType.RAISE:
                raise output.output
            return output.output

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper function determining the behavior based on artest_mode."""
            artest_mode = _get_artest_mode()
            if artest_mode == ArtestMode.DISABLE:
                return disable_mode(*args, **kwargs)
            elif artest_mode == ArtestMode.CASE:
                return case_mode(*args, **kwargs)
            elif artest_mode == ArtestMode.TEST:
                return test_mode(*args, **kwargs)
            raise ValueError(f"Unknown artest mode {artest_mode}")

        return wrapper

    return _autostub


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
    _stub_counter.clear()
    artest_mode_reset_token = _artest_mode_var.set(ArtestMode.TEST)

    test_results = []
    for path in glob(os.path.join(get_artest_root(), "*", "*")):
        fcid, tcid = path.split(os.path.sep)[-2:]

        def info_test_result(
            is_success,
            message="",
            _inputs=None,
            _expected_outputs=None,
            _actual_outputs=None,
            _func=None,
        ):
            test_results.append(TestResult(is_success, fcid, tcid, message))
            s = get_message_formatter()(
                MessageRecord(
                    is_success=is_success,
                    fcid=fcid,
                    tcid=tcid,
                    message=message,
                    inputs=_inputs,
                    expected_outputs=_expected_outputs,
                    actual_outputs=_actual_outputs,
                    func=_func,
                )
            )
            get_printer()(s)

        fcid_reset_token = _fcid_var.set(fcid)
        tcid_reset_token = _tcid_var.set(tcid)
        f_inputs = _build_path(fcid, tcid, "inputs")
        f_outputs = _build_path(fcid, tcid, "outputs")
        f_func = _build_path(fcid, tcid, "func")
        if os.path.exists(f_inputs):
            args, kwargs = _serializer.read_inputs(f_inputs)
        else:
            info_test_result(False, f"Inputs file {f_inputs} not found.")
            continue
        if os.path.exists(f_outputs):
            expected_outputs: FunctionOutput = _serializer.read(f_outputs)
        else:
            info_test_result(False, f"Outputs file {f_outputs} not found.")
            continue
        if os.path.exists(f_func):
            func = _serializer.read_func(f_func)
        else:
            info_test_result(False, f"Func file {f_func} not found.")
            continue

        actual_outputs = _get_func_output(func, args, kwargs)

        if actual_outputs.output_type != expected_outputs.output_type:
            info_test_result(
                False,
                f"Output type mismatch: {actual_outputs.output_type} != {expected_outputs.output_type}",
                _inputs=(args, kwargs),
                _expected_outputs=expected_outputs,
                _actual_outputs=actual_outputs,
                _func=func,
            )
            continue
        if not get_is_equal()(actual_outputs.output, expected_outputs.output):
            info_test_result(
                False,
                "Outputs not matched.",
                _inputs=(args, kwargs),
                _expected_outputs=expected_outputs,
                _actual_outputs=actual_outputs,
                _func=func,
            )
            continue
        info_test_result(
            True,
            _inputs=(args, kwargs),
            _expected_outputs=expected_outputs,
            _actual_outputs=actual_outputs,
            _func=func,
        )

        _fcid_var.reset(fcid_reset_token)
        _tcid_var.reset(tcid_reset_token)

    _artest_mode_var.reset(artest_mode_reset_token)

    if all([r.is_success for r in test_results]):
        get_printer()(f"Passed ({len(test_results)}/{len(test_results)})")
    else:
        get_printer()(
            f"Failed ({sum([r.is_success for r in test_results])}/{len(test_results)})"
        )
    return test_results


if __name__ == "__main__":
    main()
