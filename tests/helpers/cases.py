import functools
import sys


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                try:
                    f(*new_args)
                except Exception as e:
                    e_args = list(e.args)
                    e_args.append(f"Case: {c}")
                    e.args = tuple(e_args)
                    raise
        return wrapper
    return decorator
