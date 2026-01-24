from threading import Lock
import typing as t


class SingletonMixin:
    _singleton_instance: t.ClassVar[t.Any] = None
    _singleton_lock: t.ClassVar[Lock] = Lock()

    @classmethod
    def get_instance(cls) -> t.Self:
        return cls._singleton_instance

    def __new__(cls, *args, **kwargs) -> t.Self:
        with cls._singleton_lock:
            if cls._singleton_instance is None:
                cls._singleton_instance = object.__new__(cls)
        return cls._singleton_instance
