from os import environ
import json

class TokenProvider:
    def __init__(self):
        self.is_testing = False
    
    def enable_test(self):
        self.is_testing = True

    def load_token(self, token_key: str):
        if self.is_testing:
            self._load_test(token_key)
        
        else:
            self._load_deploy(token_key)
        
    def _load_test(self, token_key: str):
        try:
            with open('TOKEN.json', 'r', encoding='UTF-8') as f:
                return json.load(f)[token_key]
        except FileNotFoundError:
            print("[ERROR] `TOKEN.json` file is missing.")
            exit(1)
        except KeyError:
            print(f"[ERROR] `{token_key}` field in json file is missing.")
            exit(1)
    
    def _load_deploy(self, token_key: str):
        try:
            return environ[token_key]
        except KeyError:
            print(f"[ERROR] `{token_key}` is not set in your environment variables.")
            exit(1)

provider = TokenProvider()
