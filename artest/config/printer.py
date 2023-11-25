"""This module contains functions for printing objects.

Functions and Classes:
    - set_stringify_obj(func): Sets the function for converting an object to a string.
    - get_stringify_obj(): Gets the function for converting an object to a string.
    - set_message_formatter(func): Sets the function for formatting the message.
    - get_message_formatter(): Gets the function for formatting the message.
    - set_printer(func): Sets the function for printing the message.
    - get_printer(): Gets the function for printing the message.
    - MessageRecord: Represents a message record.

"""
from artest._schema import MessageRecord


def _default_stringify_obj(obj):
    return repr(obj)


_stringify_obj = _default_stringify_obj


def set_stringify_obj(func):
    """Sets the function for converting an object to a string.

    Args:
        func (function): The function for converting an object to a string.
    """
    global _stringify_obj

    if func is None:
        _stringify_obj = _default_stringify_obj
    else:
        _stringify_obj = func


def get_stringify_obj():
    """Gets the function for converting an object to a string.

    Returns:
        function: The function for converting an object to a string.
    """
    return _stringify_obj


def _default_message_formatter(message_record: MessageRecord):
    """Default message formatter.

    Args:
        message_record (MessageRecord): The message record to be formatted.

    Returns:
        str: The formatted message.
    """
    s = []
    if message_record.is_success:
        s.append(f"{'SUCCESS':10s}")
    else:
        s.append(f"{'FAIL':10s}")
    s.append(f"fc={message_record.fcid}")
    s.append(f"tc={message_record.tcid}")
    if message_record.message:
        s.append(f"msg={message_record.message}")
    if not message_record.is_success:
        if message_record.expected_outputs:
            s.append(
                f"expected: {message_record.expected_outputs.output_type} {get_stringify_obj()(message_record.expected_outputs.output)}"
            )
        if message_record.actual_outputs:
            s.append(
                f"actual: {message_record.actual_outputs.output_type} {get_stringify_obj()(message_record.actual_outputs.output)}"
            )
    s = " ".join(s)
    return f"ARTEST: {s}"


_message_formatter = _default_message_formatter


def set_message_formatter(func):
    """Sets the function for formatting the message.

    Args:
        func (function): The function for formatting the message.
    """
    global _message_formatter

    if func is None:
        _message_formatter = _default_message_formatter
    else:
        _message_formatter = func


def get_message_formatter():
    """Gets the function for formatting the message.

    Returns:
        function: The function for formatting the message.
    """
    return _message_formatter


def _default_printer(s):
    """Default printer.

    Args:
        s (str): The string to be printed.
    """
    print(s)


_printer = _default_printer


def set_printer(func):
    """Sets the function for printing the message.

    Args:
        func (function): The function for printing the message.
    """
    global _printer

    if func is None:
        _printer = _default_printer
    else:
        _printer = func


def get_printer():
    """Gets the function for printing the message.

    Returns:
        function: The function for printing the message.
    """
    return _printer
