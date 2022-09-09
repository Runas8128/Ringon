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
    @app_commands.default_permissions(
        administrator=True
    )
    async def log(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "관리자 전용 명령어입니다."
            )
        await interaction.response.send_message(
            file=discord.File('.log'),
            ephemeral=True
        )

async def setup(bot: Ringon):
    await bot.add_cog(CogDebug(bot), guild=bot.target_guild)
