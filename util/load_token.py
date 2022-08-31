"""Generalized token loader"""

from os import environ
import json

class TokenProvider:
    """Generalized token loader

    If test is enabled, provider uses "/TOKEN.json" file to load token.
    Else, it uses environment variable to load token
    """
    def __init__(self):
        self.load_token = self._load_deploy

    def enable_test(self):
        """change token loader for test"""
        self.load_token = self._load_test

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

provider = TokenProvider()
