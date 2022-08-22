from os import environ
import json

class TokenProvider:
    def __init__(self):
        self.load_token = self._load_deploy
    
    def enable_test(self):
        self.load_token = self._load_test
        
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
