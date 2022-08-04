import discord
from discord import app_commands
from discord.ext import commands

from util.utils import util
from util.myBot import MyBot

class CogOther(commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
    
    @app_commands.command(
        name='금칙어',
        description='현재 등록된 금칙어를 보여줍니다. 명령어를 사용하신 분께만 보입니다.'
    )
    async def cmdGetBlockWord(self, interaction: discord.Interaction):
        await interaction.response.send_message(', '.join(util.getBlockWord()), ephemeral=True)
    
    @app_commands.command(
        name='지연시간',
        description='현재 봇 서버와의 레이턴시를 알려줍니다. 실제 인터랙션 레이턴시와는 차이가 있을 수 있습니다.'
    )
    async def cmdGetLatency(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"현재 레이턴시는 {round(self.bot.latency*1000, 2):.2f}ms 입니다.")

async def setup(bot: MyBot):
    await bot.add_cog(CogOther(bot), guild=bot.target_guild)
