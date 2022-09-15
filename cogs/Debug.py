import discord
from discord import app_commands
from discord.ext import commands

from ringon import Ringon

class CogDebug(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot

    @app_commands.command(
        name="log",
        description="send log file"
    )
    async def log(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            file=discord.File('.log'),
            ephemeral=True
        )

async def setup(bot: Ringon):
    await bot.add_cog(CogDebug(bot), guild=bot.target_guild)
