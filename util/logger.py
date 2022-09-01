from typing import Callable
from logging import Logger

class SupportLoad:
    inited: bool

    def load(self):
        pass

def loader(logger: Logger):
    def deco(_loader: Callable):
        def inner(ref: SupportLoad):
            module_name = type(ref).__name__
            logger.info("Loading module '%s'", module_name)
            if ref.inited:
                logger.warning(
                    "Skipping loading module '%s': already loaded",
                    module_name
                )
                return
            ref.inited = True

            _loader(ref)
            logger.info("module '%s' loaded", module_name)
        return inner
    return deco
