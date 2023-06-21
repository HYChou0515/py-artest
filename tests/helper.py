import os
import shutil
from contextlib import contextmanager
from functools import wraps


def pop_all_from_list(lst):
    while lst:
        lst.pop()


def assert_test_case_files_exist(fcid, tcid):
    assert os.path.exists(f"./.artest/{fcid}/{tcid}/inputs")
    assert os.path.exists(f"./.artest/{fcid}/{tcid}/outputs")
    assert os.path.exists(f"./.artest/{fcid}/{tcid}/func")


def cleanup_test_case_files(fcid, tcid):
    shutil.rmtree(f"./.artest/{fcid}/{tcid}")


@contextmanager
def environ(target, value):
    original = os.environ.get(target)
    os.environ[target] = value
    try:
        yield
    finally:
        # Code to release resource, e.g.:
        if original is None:
            del os.environ[target]
        else:
            os.environ[target] = original


def make_test_autoreg():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with environ("ARTEST_MODE", "case"):
                func(*args, **kwargs)

        return wrapper

    return decorator
