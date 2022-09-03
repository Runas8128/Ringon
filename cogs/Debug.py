import discord
from discord import app_commands
from discord.ext import commands

from ringon import Ringon

class CogDebug(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot

    @app_commands.command(
        name="admin_only_test"
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def test(self, interaction: discord.Interaction):
        """Admin only command example.

        This command is not visible to general user.
        """
        await interaction.response.send_message(interaction.user.mention)

async def setup(bot: Ringon):
    await bot.add_cog(CogDebug(bot), guild=bot.target_guild)
