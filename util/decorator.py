from logging import Logger

def database(logger: Logger):
    def deco(cls):
        class inner(cls):
            def __init__(self, *args, **kwargs):
                self.inited = False
                super().__init__(*args, **kwargs)

            def load(self):
                if self.inited:
                    logger.warning(
                        "Skipping loading module '%s': already loaded",
                        logger.name
                    )
                    return

                logger.info("Loading module '%s'", logger.name)

                try:
                    super().load()
                    self.inited = True
                    logger.info("module '%s' loaded", logger.name)
                except Exception as exc:
                    logger.error(
                        "While loading module '%s', an exception occured.",
                        logger.name, exc_info=exc
                    )
                    raise exc from None
        return inner
    return deco
