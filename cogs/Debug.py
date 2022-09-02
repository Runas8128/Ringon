from discord.ext import commands

from ringon import Ringon

class CogDebug(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def cmg_dbg(
        self, ctx: commands.Context
    ):
        pass

async def setup(bot: Ringon):
    await bot.add_cog(CogDebug(bot), guild=bot.target_guild)
