"""Simple ringon instance factory."""

from typing import List, Optional

import discord
from discord.ext import commands

from util.load_token import provider

class Ringon(commands.Bot):
    """Simple ringon instance factory.

    ### Attributes ::
        is_testing (bool):
            indicates if the bot instance is in testing mode.
        test_cogs (List[str], optional):
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
        self.all_cogs = test_cogs or [
            'Events',
            'DeckList', 'Detect', 'Birthday',
            'Check', 'Other',
            'Backup',
        ]

    def run(self):
        """get token automatically and run bot."""
        token = provider.load_token('discord')
        super().run(token)

    async def setup_hook(self):
        app_info = await self.application_info()
        self.owner_id = app_info.owner.id

        for cogName in self.all_cogs:
            await self._load(cogName)

        if self.is_testing:
            await self._load('Debug')

        await self.tree.sync(guild=self.target_guild)

    async def _load(self, name: str):
        """|coro|

        this coroutine loads extension, ignore `NotLoaded` exception.
        """
        try:
            await self.bot.load_extension('cogs.' + name)
            print(f"Loaded {name}")
        except commands.ExtensionAlreadyLoaded:
            print(f"Skipping loading cog {name}: Already loaded")
