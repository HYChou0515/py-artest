__all__ = ["autoreg", "automock", "set_pickler"]
__version__ = "0.1.2"

from .artest import automock, autoreg
from .config.pickler import set_pickler
