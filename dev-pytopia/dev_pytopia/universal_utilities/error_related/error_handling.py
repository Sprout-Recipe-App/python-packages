from asyncio import iscoroutinefunction
from contextlib import asynccontextmanager
from functools import wraps
from inspect import isasyncgenfunction, isclass, signature
from traceback import format_exc

from ...services.logger.logger import Logger


def with_error_handling(
    target=None, *, exclude_methods=None, include_private=True, service_name=None, logger=None
):
    error_logger = logger or Logger(log_level="ERROR")

    def truncate(string, limit=800):
        return string if len(string) <= limit else f"{string[:limit]}...(truncated)"

    def _wrap_function(function, service_name_override=None):
        strip_first = next(iter(signature(function).parameters), None) in {"self", "cls"}

        def report_error(exception, args=(), kwargs=None):
            service = service_name_override or (
                getattr(args[0], "__name__", type(args[0]).__name__) if args else "Service"
            )
            error_logger.error(
                f"[{service}] {function.__name__} raised {type(exception).__name__}: {exception}\n"
                f"Args: {truncate(repr(args[1:] if strip_first and args else args))}\n"
                f"Kwargs: {truncate(repr(kwargs or {}))}\nTraceback:\n{format_exc()}",
                stacklevel=3,
            )

        if isasyncgenfunction(function):

            @wraps(function)
            @asynccontextmanager
            async def wrapper(*args, **kwargs):
                try:
                    async for value in function(*args, **kwargs):
                        yield value
                except Exception as exception:
                    report_error(exception, args, kwargs)
                    raise

            return wrapper

        if iscoroutinefunction(function):

            @wraps(function)
            async def wrapper(*args, **kwargs):
                try:
                    return await function(*args, **kwargs)
                except Exception as exception:
                    report_error(exception, args, kwargs)
                    raise

            return wrapper

        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as exception:
                report_error(exception, args, kwargs)
                raise

        return wrapper

    def _wrap_class(class_to_wrap):
        service = service_name or class_to_wrap.__name__
        for name, method in class_to_wrap.__dict__.items():
            if name.startswith("__" if include_private else "_") or (exclude_methods and name in exclude_methods):
                continue
            if isinstance(method, classmethod):
                setattr(class_to_wrap, name, classmethod(_wrap_function(method.__func__, service)))
            elif callable(method) and not isinstance(method, (staticmethod, property)) and not isclass(method):
                setattr(class_to_wrap, name, _wrap_function(method, service))
        return class_to_wrap

    return (
        _wrap_class(target)
        if isclass(target)
        else (_wrap_class if target is None else _wrap_function(target, service_name))
    )
