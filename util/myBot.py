from typing import List

import discord
from discord.ext import commands

from .load_token import load_token

class MyBot(commands.Bot):
    def __init__(self, is_testing: bool, testCogs: List[str] = []):
        super().__init__(
            command_prefix='!',
            help_command=None,
            intents=discord.Intents.all(),
            case_insensitive=True
        )

        self.is_testing = is_testing
        self.target_guild = discord.Object(
            id=823359663973072957 if self.is_testing else 758478112979288094
        )
        self.testCogs = testCogs
    
    def run(self):
        """get token automatically and run bot.
        if `429 Too many request` error raises,
        then clear console and notice how long we should wait.
        """
        try:
            token = load_token('discord', self.is_testing)
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
        appInfo = await self.application_info()
        self.owner_id = appInfo.owner.id

        await self.load_extension('cogs.CogManager')
        await self.tree.sync(guild=self.target_guild)
