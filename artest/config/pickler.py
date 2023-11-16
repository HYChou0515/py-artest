_pickler = None


def set_pickler(pkl):
    global _pickler
    _pickler = pkl


def get_pickler():
    global _pickler
    if _pickler is None:
        try:
            import dill

            _pickler = dill
        except ImportError:
            import pickle

            _pickler = pickle
    return _pickler
