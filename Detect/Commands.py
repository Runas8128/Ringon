import discord
from discord.ext import commands

from .Helper import detect
from util.embedManager import embedManager

class CogDetect(commands.Cog, name='일부감지'):
    """
    메시지의 일부를 감지하게 하는 명령어 카테고리입니다.
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        msg: str = message.content

        rst = detect.tryGet(msg)
        if rst != None:
            await message.channel.trigger_typing()
            await message.channel.send(rst)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot: return

        await embedManager.proceedReaction(reaction.message.id, reaction.emoji)
    
    @commands.command(name='잊어')
    async def RG_Forget(self, ctx: commands.Context):
        await ctx.send("해당 명령어는 더 이상 사용되지 않습니다. 개발자에게 직접 삭제요청을 해주세요!")
    
    @commands.command(
        name='능지',
        brief='링곤이가 배운 총 문장의 개수를 보여줍니다.',
        description='링곤이가 배운 총 문장의 개수를 보여줍니다.',
        usage='!능지'
    )
    async def RG_Neungji(self, ctx: commands.Context):
        await ctx.send(f"링곤사전을 보니, 저의 아이큐는 {detect.getFullCount()}이라고 하네요!")
    
    @commands.command(
        name='배운거',
        brief='링곤이가 배운 문장을 모두 알려줍니다.',
        description='링곤이가 배운 문장을 모두 알려줍니다. 10개씩 끊어서 보여주며, 이모지를 눌러서 페이지별로 이동이 가능합니다.',
        usage='!배운거'
    )
    async def RG_Studied(self, ctx: commands.Context):
        await embedManager.make(detect.getFullDetect(), ctx.channel)
    
    @commands.command(
        name='센서민감도',
        brief='링곤이가 감지할 총 문장의 개수를 보여줍니다.',
        description='링곤이가 감지할 총 문장의 개수를 보여줍니다.',
        usage='!센서민감도'
    )
    async def RG_Neungji(self, ctx: commands.Context):
        await ctx.send(f"링곤사전을 보니, 저의 센서민감도는 {detect.getPartCount()}이라고 하네요!")
    
    @commands.command(
        name='센서기록',
        brief='링곤이가 감지할 문장을 모두 알려줍니다.',
        description='링곤이가 감지할 문장을 모두 알려줍니다. 10개씩 끊어서 보여주며, 이모지를 눌러서 페이지별로 이동이 가능합니다.',
        usage='!센서기록'
    )
    async def RG_Sensor(self, ctx: commands.Context):
        await embedManager.make(detect.getPartCount(), ctx.channel)
