"""Simple ringon instance factory."""

from typing import List, Optional

import discord
from discord.ext import commands

from .load_token import provider

class MyBot(commands.Bot):
    """Simple ringon instance factory.

    ### Attributes ::
        is_testing (bool):
            indicates if the bot instance is in testing mode.
        test_cogs (list of str, optional):
            indicates list of cog name to test.
            If this parameter is missing, load all cogs (pre-defined).
    """
    def __init__(self, is_testing: bool, test_cogs: Optional[List[str]] = None):
        super().__init__(
            command_prefix='!',
            help_command=None,
            intents=discord.Intents.all(),
            case_insensitive=True
        )

        self.is_testing = is_testing

        if self.is_testing:
            provider.enable_test()

        self.target_guild = discord.Object(
            id=823359663973072957 if self.is_testing else 758478112979288094
        )
        self.test_cogs = test_cogs

    def run(self):
        """get token automatically and run bot."""
        token = provider.load_token('discord')
        super().run(token)

    async def setup_hook(self):
        app_info = await self.application_info()
        self.owner_id = app_info.owner.id

        await self.load_extension('cogs.CogManager')
        await self.tree.sync(guild=self.target_guild)
