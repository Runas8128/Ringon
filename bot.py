import discord
from discord.ext import commands

def getToken(is_testing: bool):
    """Load token with proper way(json loading vs environment variable)"""

    if is_testing:
        import json

        try:
            with open('TOKEN.json', 'r', encoding="UTF-8") as f:
                return json.load(f)["TOKEN"]
        except FileNotFoundError:
            print("[ERROR] `TOKEN.json` file is missing.")
            exit(1)
        except KeyError:
            print("[ERROR] `TOKEN` field in json file is missing.")
            exit(1)
    
    else:
        from os import environ

        try:
            return environ["TOKEN"]
        except KeyError:
            print("[ERROR] TOKEN is not set in your environment variables.")
            exit(1)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            help_command=None,
            intents=discord.Intents.all(),
            case_insensitive=True
        )

        self.is_testing = False
        self.target_guild = 758478112979288094
    
    def enable_test(self):
        """Enable `is_testing` flag. This function should be called before run bot"""
        self.is_testing = True
        self.target_guild = 823359663973072957
    
    def run(self):
        """get token automatically and run bot.
        if `429 Too many request` error raises,
        then clear console and notice how long we should wait.
        """
        try:
            token = getToken(self.is_testing)
            super().run(token)
        except discord.errors.HTTPException as E:
            if E.code != 429: raise

            from os import system, name
            system('cls' if name == 'nt' else 'clear')
            
            sec = int(E.response.headers['Retry-After'])

            h = sec // 3600
            sec -= h * 3600
            m = sec // 60
            sec -= m * 60
            s = sec
            
            print(f"Retry-After: {h}h {m}m {s}s")
    
    async def setup_hook(self):
        await self.load_extension('util.CogManager')

        if self.is_testing:
            await self.load_extension('util.Debug')
        await self.tree.sync(guild=self.target_guild)

bot = Bot()
