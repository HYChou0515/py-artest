from uuid import uuid4


class TestCaseIdGenerator:
    def __init__(self):
        self._gen = None

    def __next__(self):
        if self._gen is None:
            self._gen = _test_case_id_generator
        return next(self._gen)

    def __iter__(self):
        return self


def default_test_case_id_generator():
    while True:
        yield f"tc-{str(uuid4())[:8]}"


_test_case_id_generator = default_test_case_id_generator()


def set_test_case_id_generator(gen=None):
    global _test_case_id_generator
    _test_case_id_generator = gen


test_case_id_generator = TestCaseIdGenerator()
