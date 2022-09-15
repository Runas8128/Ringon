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
    
    @app_commands.command(
        name="prune"
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def cmdPurgeMessage(self, interaction: discord.Interaction,
        count: int
    ):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "관리자 전용 명령어입니다."
            )
        if count <= 0:
            return await interaction.response.send_message(
                "자연수를 입력해주세요."
            )
        await interaction.response.defer()
        await interaction.channel.purge(count)
        await interaction.followup.send_message("Done.")

    @app_commands.command(
        name="kill"
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def cmdKill(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "관리자 전용 명령어입니다."
            )
        await interaction.response.send_message("강제종료중...")
        await self.bot.close()

async def setup(bot: Ringon):
    await bot.add_cog(CogDebug(bot), guild=bot.target_guild)
