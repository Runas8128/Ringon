def load_token(token_key: str, is_testing: bool):
    if is_testing:
        try:
            with open('TOKEN.json', 'r', encoding='UTF-8') as f:
                return json.load(f)[token_key]
        except FileNotFoundError:
            print("[ERROR] `TOKEN.json` file is missing.")
            exit(1)
        except KeyError:
            print(f"[ERROR] `{token_key}` field in json file is missing.")
            exit(1)
    
    else:
        from os import environ

        try:
            return environ[token_key]
        except KeyError:
            print(f"[ERROR] `{token_key}` is not set in your environment variables.")
            exit(1)
