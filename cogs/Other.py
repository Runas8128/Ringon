import discord
from discord import app_commands
from discord.ext import commands

from util.utils import util
from ringon import Ringon

class CogOther(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        util.load()

    @app_commands.command(
        name='금칙어',
        description=(
            '현재 등록된 금칙어를 보여줍니다. '
            '명령어를 사용하신 분께만 보입니다.'
        )
    )
    async def cmdGetBlockWord(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            ', '.join(util.block_words), ephemeral=True
        )

    @app_commands.command(
        name='지연시간',
        description=(
            '현재 봇 서버와의 레이턴시를 알려줍니다. '
            '실제 인터랙션 레이턴시와는 차이가 있을 수 있습니다.'
        )
    )
    async def cmdGetLatency(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"현재 레이턴시는 {round(self.bot.latency*1000, 2):.2f}ms 입니다."
        )

    @app_commands.command(
        name='생존신고',
        description='링곤이가 살아있는지 확인해줍니다.'
    )
    async def cmdCheckAlive(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "살아있어요!",
            ephemeral=True
        )

async def setup(bot: Ringon):
    await bot.add_cog(CogOther(bot), guild=bot.target_guild)
