import os
from dataclasses import dataclass
from glob import glob
from typing import Literal, Union

from ._paths import get_artest_root


@dataclass
class _TestCaseQuotaConfig:
    max_count: Union[int, Literal['inf']] = 'inf'


class _TestCaseQuota:
    def __init__(self, quota_config: _TestCaseQuotaConfig):
        self._quota_config = quota_config

    def can_add_test_case(self, fcid):
        cur_count = len(glob(os.path.join(get_artest_root(), fcid, "*", "func")))
        return self._quota_config.max_count == 'inf' or cur_count < self._quota_config.max_count


_test_case_quota_config = _TestCaseQuotaConfig()
_test_case_quota = _TestCaseQuota(_test_case_quota_config)


def set_test_case_quota(*, max_count: Union[int, Literal['inf']] = None):
    global _test_case_quota_config
    global _test_case_quota

    if max_count is not None:
        _test_case_quota_config.max_count = max_count

    _test_case_quota = _TestCaseQuota(_test_case_quota_config)


def get_test_case_quota():
    return _test_case_quota
