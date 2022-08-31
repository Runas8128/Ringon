import discord
from discord import app_commands
from discord.ext import commands

from util.ringon import MyBot

class CogManager(commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.all_cog = self.bot.test_cogs or [
            'Events',
            'DeckList', 'Detect', 'Birthday',
            'Check', 'Other',
            'Backup',
        ]
    
    async def load_all(self):
        for cogName in self.all_cog: await self._load(cogName)
        if self.bot.is_testing: await self._load('Debug')
        
        await self.bot.tree.sync(guild=self.bot.target_guild)
    
    async def _load(self, name: str):
        """|coro|

        this coroutine loads extension, ignore `NotLoaded` exception.
        """
        try:
            await self.bot.load_extension('cogs.' + name)
            print(f"Loaded {name}")
        except commands.ExtensionAlreadyLoaded:
            print(f"Skipping loading cog {name}: Already loaded")

async def setup(bot: MyBot):
    manager = CogManager(bot)
    await manager.load_all()

    await bot.add_cog(manager, guild=bot.target_guild)
