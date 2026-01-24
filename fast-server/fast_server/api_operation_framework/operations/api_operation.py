import re

from dev_pytopia import Operation


class APIOperation(Operation):
    ENDPOINT_PATH: str
    METHOD = "GET"
    LOG_REQUESTS = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "ENDPOINT_PATH" not in cls.__dict__:
            name = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", cls.__name__)
            cls.ENDPOINT_PATH = "/" + re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name).lower()
