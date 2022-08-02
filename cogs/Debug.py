from typing import List
import asyncio
from datetime import timedelta
from time import time

import discord
from discord.ext import commands

from util.myBot import MyBot

class CogDebug(commands.Cog):    
    def __init__(self, bot: MyBot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def dbgCmd(self, ctx: commands.Context):
        pass

async def setup(bot: MyBot):
    await bot.add_cog(CogDebug(bot), guild=bot.target_guild)
