import functools
from flask import current_app as app


def disable_if_testing(decorator):
    def decorator_dit(func):
        @functools.wraps(func)
        def wrapper_dit(*args, **kwargs):
            if app.config['TESTING'] is True:
                return func(*args, **kwargs)
            else:
                return decorator(func)(*args, **kwargs)
        return wrapper_dit
    return decorator_dit
