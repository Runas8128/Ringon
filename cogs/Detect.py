import discord
from discord import app_commands
from discord.ext import commands

from util.detect import detect
from util.view import EmbedView
from ringon import Ringon

class CogDetect(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        rst = detect[message.content]
        if rst is not None:
            await message.channel.typing()
            await message.channel.send(rst)

    @app_commands.command(
        name="능지",
        description="링곤이가 배운 단어들이 몇 개인지 알려줍니다. 전체 단어 목록은 `배운거` 명령어로 알 수 있습니다."
    )
    async def cmdGetIQ(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"링곤사전을 보니, 저의 아이큐는 {len(detect)}이라고 하네요!")

    @app_commands.command(
        name="배운거",
        description="링곤이의 단어장을 보여줍니다. 추가/삭제는 개발자에게 직접 요청해주시기 바랍니다."
    )
    async def cmdGetFullWordMap(self, interaction: discord.Interaction):
        view = EmbedView(*detect.get_list())
        await interaction.response.send_message(embed=view.make_embed(), view=view)

async def setup(bot: Ringon):
    await bot.add_cog(CogDetect(bot), guild=bot.target_guild)
