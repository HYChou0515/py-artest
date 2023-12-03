from artest import autoreg

from .hello_id import hello_id


@autoreg(hello_id)
def hello(say, to):
    return f"{say} {to}! This is a different string."