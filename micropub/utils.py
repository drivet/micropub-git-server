import os
import functools
from flask import current_app as app


def disable_if_testing(decorator):
    def decorator_dit(func):
        @functools.wraps(func)
        def wrapper_dit(*args, **kwargs):
            if app.config.get('TESTING', False) is True:
                return func(*args, **kwargs)
            else:
                return decorator(func)(*args, **kwargs)
        return wrapper_dit
    return decorator_dit


def get_root():
    return os.environ.get('MICROPUB_ROOT', '/data')
