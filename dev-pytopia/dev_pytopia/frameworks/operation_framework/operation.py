from abc import ABC, abstractmethod


class Operation(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs): ...
    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)

    def __await__(self):
        return self.execute().__await__()
