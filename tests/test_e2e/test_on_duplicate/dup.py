from artest import autoreg

from .hello_id import dup_id


@autoreg(dup_id)
def dup1(x):
    return x + 1


@autoreg(dup_id)
def dup2(x):
    return x + 2
