import discord
from discord import app_commands
from discord.ext import commands

from util.detect import detect
from util.view import EmbedView
from util.myBot import MyBot

class CogDetect(commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        rst = detect.tryGet(message.content)
        if rst != None:
            await message.channel.trigger_typing()
            await message.channel.send(rst)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if not user.bot:
            await embedManager.proceedReaction(reaction.message.id, reaction.emoji)
    
    @app_commands.command(
        name="능지",
        description="링곤이가 배운 단어들이 몇 개인지 알려줍니다. 전체 단어 목록은 `배운거` 명령어로 알 수 있습니다."
    )
    async def cmdGetIQ(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"링곤사전을 보니, 저의 아이큐는 {detect.getFullCount()}이라고 하네요!"
        )
    
    @app_commands.command(
        name="배운거",
        description="링곤이의 단어장을 보여줍니다. 추가/삭제는 개발자에게 직접 요청해주시기 바랍니다."
    )
    async def cmdGetWordMap(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            view=EmbedView(interaction, *detect.getFullDetect())
        )
    
    @app_commands.command(
        name="센서민감도",
        description="링곤이가 감지할 단어들이 몇 개인지 알려줍니다. 전체 단어 목록은 `센서기록` 명령어로 알 수 있습니다."
    )
    async def cmdGetSensitivity(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"링곤사전을 보니, 저의 센서민감도는 {detect.getPartCount()}이라고 하네요!"
        )
    
    @app_commands.command(
        name="센서기록",
        description="링곤이가 일부감지할 친구들을 보여줍니다. 추가/삭제는 개발자에게 직접 요청해주시기 바랍니다."
    )
    async def cmdGetWordMap(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            view=EmbedView(interaction, *detect.getPartDetect())
        )

async def setup(bot: MyBot):
    await bot.add_cog(CogDetect(bot), guild=bot.target_guild)
