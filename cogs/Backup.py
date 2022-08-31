from os import listdir
from os.path import isfile, join
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from ringon import Ringon

class CogBackup(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot
        self.channel: discord.TextChannel = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = self.bot.get_channel(1011058755854663720)

    async def SendBackupMessage(self, now: datetime):
        await self.channel.send(
            content=f"{now.strftime('%Y/%m/%d')} SQLite DB backup",
            files=[
                discord.File(join('DB', f))
                for f in listdir('DB') if isfile(join('DB', f))
            ]
        )

    @tasks.loop(hours=1.0)
    async def backupDB(self):
        now = datetime.now()
        if (
            now - now.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds() < 1 * 60 * 60:
            await self.SendBackupMessage(now)

    @app_commands.command(
        name="db_backup",
        description="DB파일을 백업합니다. DB 기반 수정 이후 삭제될 명령어입니다."
    )
    async def cmdBackupDB(self, interaction: discord.Interaction):
        await self.SendBackupMessage(datetime.now())
        await interaction.response.send_message(
            "백업 파일을 전송했습니다!",
            ephemeral=True
        )

async def setup(bot: Ringon):
    await bot.add_cog(CogBackup(bot), guild=bot.target_guild)
