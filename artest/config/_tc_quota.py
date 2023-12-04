import dataclasses
import os
from glob import glob
from typing import Literal, Optional, Union

from ..types import ConfigTestCaseQuota
from ._paths import get_artest_root


class _TestCaseQuota:
    def __init__(self, quota_config: ConfigTestCaseQuota):
        self._quota_config = quota_config
        if self._quota_config.max_count is None:
            self._quota_config.max_count = "inf"

    def can_add_test_case(self, fcid):
        cur_count = len(glob(os.path.join(get_artest_root(), fcid, "*", "func")))
        return (
            self._quota_config.max_count == "inf"
            or cur_count < self._quota_config.max_count
        )


_default_test_case_quota_config = ConfigTestCaseQuota()
_func_test_case_quota_config: dict[str, ConfigTestCaseQuota] = {}
_func_test_case_quota: dict[str, _TestCaseQuota] = {}


def reset_all_test_case_quota():
    """Reset all test case quota."""
    global _func_test_case_quota
    global _func_test_case_quota_config
    global _default_test_case_quota_config
    _func_test_case_quota = {}
    _func_test_case_quota_config = {}
    _default_test_case_quota_config = ConfigTestCaseQuota()


def set_test_case_quota(
    fcid: str = None,
    *,
    quota: Optional[ConfigTestCaseQuota] = None,
    max_count: Union[int, Literal["inf"]] = None
):
    """Set test case quota for a function.

    If fcid is None, set default test case quota.

    Args:
        fcid (str, optional): The function id. Defaults to None.
        quota (ConfigTestCaseQuota, optional): The test case quota config. Defaults to None.
            If quota is not None, other fields (e.g. max_count) will be ignored.
        max_count (Union[int, Literal['inf']], optional): The max count of test cases. Defaults to None.
    """
    global _default_test_case_quota_config
    if fcid is None:
        quota_config = _default_test_case_quota_config
    else:
        if fcid not in _func_test_case_quota_config:
            _func_test_case_quota_config[fcid] = dataclasses.replace(
                _default_test_case_quota_config
            )
        quota_config = _func_test_case_quota_config[fcid]

    if quota is None:
        # update each field of quota config
        if max_count is not None:
            quota_config.max_count = max_count
    else:
        # update quota config
        quota_config = quota

    if fcid is None:
        # update default test case quota
        _default_test_case_quota_config = quota_config
    else:
        # update test case quota config
        _func_test_case_quota_config[fcid] = quota_config
        # update test case quota
        _func_test_case_quota[fcid] = _TestCaseQuota(quota_config)


def get_test_case_quota(fcid: str):
    """Get test case quota for a function.

    If the function has registered a test case quota, return it.
    If no, but the function has registered a test case quota config,
        create and register a test case quota with the config and return it.
    If no, create and register a test case quota with the default config and return it.
    """
    if fcid in _func_test_case_quota:
        # return registered test case quota
        return _func_test_case_quota[fcid]
    if fcid in _func_test_case_quota_config:
        # create and register test case quota with registered config
        _test_case_quota = _TestCaseQuota(_func_test_case_quota_config[fcid])
        _func_test_case_quota[fcid] = _test_case_quota
        return _test_case_quota
    # create and register test case quota with default config
    tc_quota = _TestCaseQuota(_default_test_case_quota_config)
    _func_test_case_quota[fcid] = tc_quota
    return tc_quota
