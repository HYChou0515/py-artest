"""Module handling actions for duplicate func_ids.

This module manages the actions to take when encountering duplicate func_ids within the artest package.
The main functions provided here allow setting and retrieving the action to be taken when such duplicates occur.

Functions:
- `set_on_func_id_duplicate(action: Optional[OnFuncIdDuplicateAction] = None)`: Sets the action to take when a duplicate func_id is found. If no action is provided, it defaults to raising an exception.
- `get_on_func_id_duplicate() -> OnFuncIdDuplicateAction`: Retrieves the action set for handling duplicate func_ids.

Typically, the default action is to raise an exception when a duplicate func_id is encountered.
"""

from typing import Optional

from artest.types import OnFuncIdDuplicateAction

_default_on_duplicate = OnFuncIdDuplicateAction.RAISE


def set_on_func_id_duplicate(action: Optional[OnFuncIdDuplicateAction] = None):
    """Sets the action when a duplicate func_id is found.

    Args:
        action (OnFuncIdDuplicateAction): The action when a duplicate func_id is found.
            If action is None, the default action is set to raise an exception.
    """
    global _default_on_duplicate
    if action is None:
        _default_on_duplicate = OnFuncIdDuplicateAction.RAISE
    else:
        _default_on_duplicate = action


def get_on_func_id_duplicate():
    """Gets the action when a duplicate func_id is found.

    Returns:
        OnFuncIdDuplicateAction: The action when a duplicate func_id is found.
    """
    return _default_on_duplicate
