"""Group of debug commands."""

from discord.ext import commands

from ringon import Ringon

class CogDebug(commands.Cog):
    """Group of debug commands."""
    def __init__(self, bot: Ringon):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def cmg_dbg(self, ctx: commands.Context):
        """Debug command sample.

        All of debug commands should have `is_owner` check decorator.

        ### Args ::
            ctx (discord.ext.commands.Context):
                context of your debug command
        """

async def setup(bot: Ringon):
    """Add debug command group to bot."""
    await bot.add_cog(CogDebug(bot), guild=bot.target_guild)
