from typing import Callable
from logging import Logger

class SupportLoad:
    inited: bool

    def load(self):
        pass

def loader(logger: Logger):
    def deco(_loader: Callable):
        def inner(ref: SupportLoad):
            if ref.inited:
                logger.warning(
                    "Skipping loading module '%s': already loaded",
                    logger.name
                )
                return

            logger.info("Loading module '%s'", logger.name)

            try:
                _loader(ref)
                ref.inited = True
                logger.info("module '%s' loaded", logger.name)
            except Exception as exc:
                logger.error(
                    "While loading module '%s', an exception occured.",
                    logger.name, exc_info=exc
                )
                raise exc from None
        return inner
    return deco
