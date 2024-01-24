from typing import *
from functools import wraps


def override(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
