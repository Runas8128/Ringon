from typing import Callable
from logging import Logger

class SupportLoad:
    inited: bool

    def load(self):
        pass

def loader(
    logger: Logger,
    start_msg: str = "Loading module '%s'",
    end_msg: str = "module '%s' loaded"
):
    def deco(_loader: Callable):
        def inner(ref: SupportLoad):
            logger.info(start_msg, type(ref).__name__)
            if ref.inited:
                return
            ref.inited = True

            _loader(ref)
            logger.info(end_msg, type(ref).__name__)
        return inner
    return deco
