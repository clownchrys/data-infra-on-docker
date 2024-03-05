from typing import *
from functools import wraps
import os

from common.enum import ApiEnvEnum


def use_mockup(*, return_value: Any, target: List[ApiEnvEnum] = [ApiEnvEnum.DEV]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if os.getenv("API_ENV", ApiEnvEnum.DEV) in target:
                return return_value
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator
    