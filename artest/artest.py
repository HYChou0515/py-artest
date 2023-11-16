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
    return os.environ.get("ARTEST_MODE", "disable")


class TestCaseSerializer:
    @staticmethod
    def dump(obj, fp):
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
        return get_pickler().dumps(obj)

    @staticmethod
    def load(fp):
        return get_pickler().load(fp)

    def save(self, obj, path):
        dirpath = os.path.dirname(path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(path, "wb") as f:
            self.dump(obj, f)

    def save_inputs(self, inputs: dict[str], path):
        assert isinstance(inputs, dict)
        return self.save(inputs, path)

    def save_func(self, func, path):
        return self.save(func, path)

    def read(self, path):
        with open(path, "rb") as f:
            return self.load(f)

    def read_inputs(self, path):
        return self.read(path)

    def read_func(self, path):
        return self.read(path)

    def calc_hash(self, obj):
        return hashlib.sha256(self.dumps(obj)).hexdigest()[10:20]


def build_path(fcid, tcid, basename):
    return os.path.join(ARTEST_ROOT, fcid, tcid, basename)


AUTOREG_REGISTERED = set()
AUTOMOCK_REGISTERED = set()
test_stack = []


def autoreg(func_id: str):
    """Auto Regression Test Decorator
    This decorator is used to create regression tests automatically during runtime.
    These created test cases are saved in a directory and can be tested later.

    Algorithm:
    # Under Case Mode
    1.  created a test case id and push to the test stack
    2.  run the function
    2.1   if the sub-function is decorated with autoreg, then run recursively
    2.2   if the sub-function is decorated with automock, then
    2.3     calculate the input hash
    2.4     run the function
    2.4     for each caller-fcid,tcid in the stack
    2.5       save output under /caller-fcid/tcid/mock/fcid.order.inputhash.output
    3.  save the serialized input,output under /fcid/tcid/input,output
    4.  pop the test stack
    # Under Test Mode
    1.  Given fcid and tcid inferred from the directory structure
    2.  load the input,output from /fcid/tcid/input,output
    3.  run the function
    3.1   if the sub-function is decorated with autoreg, then run the function like a normal one
    3.2   if the sub-function is decorated with automock, then
    3.3     calculate the input hash
    3.4     load the output from /caller_fcid/tcid/mock/fcid.order.inputhash.output
    4.  compare the output with the loaded one
    :param func_id:
    :return:
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
            f_inputs = build_path(func_id, tcid, "inputs")
            f_outputs = build_path(func_id, tcid, "outputs")
            f_func = build_path(func_id, tcid, "func")
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
    func_id = str(func_id)
    if func_id in AUTOMOCK_REGISTERED:
        raise ValueError(f"Function {func_id} is already registered in automock.")
    AUTOMOCK_REGISTERED.add(func_id)

    serializer = TestCaseSerializer()
    counts = {}

    def _automock(func):
        def disable_mode(*args, **kwargs):
            return func(*args, **kwargs)

        def _basename(func_id, call_count, input_hash):
            return os.path.join("mock", f"{func_id}.{call_count}.{input_hash}.output")

        def case_mode(*args, **kwargs):
            arguments = inspect.getcallargs(func, *args, **kwargs)
            input_hash = serializer.calc_hash(arguments)
            result = func(*args, **kwargs)
            for caller_fcid, tcid in test_stack:
                call_count = counts.get((caller_fcid, tcid), 0)
                counts[(caller_fcid, tcid)] = call_count + 1
                serializer.save(
                    result,
                    build_path(
                        caller_fcid,
                        tcid,
                        _basename(func_id, call_count, input_hash),
                    ),
                )
            return result

        def test_mode(*args, **kwargs):
            caller_fcid = os.environ["__ARTEST_FCID"]
            tcid = os.environ["__ARTEST_TCID"]

            call_count = counts.get((caller_fcid, tcid), 0)
            counts[(caller_fcid, tcid)] = call_count + 1

            arguments = inspect.getcallargs(func, *args, **kwargs)
            input_hash = serializer.calc_hash(arguments)
            path = build_path(
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


def info(s="", *args, **kwargs):
    print(f"ARTEST: {s}", *args, **kwargs)


def main():
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
            info(" ".join(s))

        os.environ["__ARTEST_FCID"] = fcid
        os.environ["__ARTEST_TCID"] = tcid
        f_inputs = build_path(fcid, tcid, "inputs")
        f_outputs = build_path(fcid, tcid, "outputs")
        f_func = build_path(fcid, tcid, "func")
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
            info_test_result(False, f"Outputs not matched.")
            continue
        info_test_result(True)

    del os.environ["__ARTEST_FCID"]
    del os.environ["__ARTEST_TCID"]
    del os.environ["ARTEST_MODE"]
    if orig_artest_mode is not None:
        os.environ["ARTEST_MODE"] = orig_artest_mode


if __name__ == "__main__":
    main()
