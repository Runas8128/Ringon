from typing import Callable, Any, TypeVar
from collections.abc import Coroutine
import logging
import inspect

Coro = TypeVar('Coro', bound=Callable[..., Coroutine[Any, Any, Any]])

class SupportLoad:
    inited: bool

    async def load(self):
        pass

def loader(logger: logging.Logger):
    def deco(_loader: Coro):
        if not inspect.iscoroutinefunction(_loader):
            logger.error(
                "Skipping loading module '%s': Loader is not a coroutine function",
                logger.name
            )

        async def inner(ref: SupportLoad):
            if ref.inited:
                logger.warning(
                    "Skipping loading module '%s': already loaded",
                    logger.name
                )
                return

            logger.info("Loading module '%s'", logger.name)
            ref.inited = True

            await _loader(ref)
            logger.info("module '%s' loaded", logger.name)
        return inner
    return deco
