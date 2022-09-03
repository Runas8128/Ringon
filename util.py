from os import environ
from logging import Logger
import json

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

class TokenProvider:
    """Generalized token loader

    If test is enabled, provider uses "/TOKEN.json" file to load token.
    Else, it uses environment variable to load token
    """
    def __init__(self):
        self.test = False
        self.load_token = self._load_deploy

    def __getitem__(self, token_key: str):
        """Token loader proxy.

        ### Returns ::
            Token value that proxy returns.
        """

        return (
            self._load_test if self.test else self._load_deploy
        )(token_key)

    def _load_test(self, token_key: str):
        """Load token from "/TOKEN.json" file.

        ### Args ::
            token_key (str):
                target key stored in "/TOKEN.json" file.

        ### Returns ::
            stored token value.

        ### Raises ::
            FileNotFoundError:
                "TOKEN.json" file is not in root directory.
            KeyError:
                Target token key is not in json file.
        """
        try:
            with open('TOKEN.json', 'r', encoding='UTF-8') as _fp:
                return json.load(_fp)[token_key]
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "[ERROR] `TOKEN.json` file is missing."
            ) from exc
        except KeyError as exc:
            raise KeyError(
                f"[ERROR] `{token_key}` field in json file is missing."
            ) from exc

    def _load_deploy(self, token_key: str):
        """Load token from environment variables.

        ### Args ::
            token_key (str):
                target key stored in environment variables.

        ### Returns ::
            stored token value.

        ### Raises ::
            KeyError:
                Target token key is not in environment variables.
        """
        try:
            return environ[token_key]
        except KeyError as exc:
            raise KeyError(
                f"[ERROR] `{token_key}` is not set in your environment variables."
            ) from exc

token = TokenProvider()
