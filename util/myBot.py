from typing import List

import discord
from discord.ext import commands

from .load_token import provider

class MyBot(commands.Bot):
    def __init__(self, is_testing: bool, testCogs: List[str] = []):
        super().__init__(
            command_prefix='!',
            help_command=None,
            intents=discord.Intents.all(),
            case_insensitive=True
        )

        self.is_testing = is_testing

        if self.is_testing: provider.enable_test()
        
        self.target_guild = discord.Object(
            id=823359663973072957 if self.is_testing else 758478112979288094
        )
        self.testCogs = testCogs
    
    def run(self):
        """get token automatically and run bot."""
        token = provider.load_token('discord')
        super().run(token)
    
    async def setup_hook(self):
        appInfo = await self.application_info()
        self.owner_id = appInfo.owner.id

        await self.load_extension('cogs.CogManager')
        await self.tree.sync(guild=self.target_guild)
