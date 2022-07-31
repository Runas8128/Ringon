import discord
from discord.ext import commands

from myBot import MyBot
from .Helper import detect
from util.embedManager import embedManager

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
    
    @commands.command(name='잊어')
    async def RG_Forget(self, ctx: commands.Context):
        await ctx.send("해당 명령어는 더 이상 사용되지 않습니다. 개발자에게 직접 삭제요청을 해주세요!")
    
    @commands.command(name='능지')
    async def RG_Neungji(self, ctx: commands.Context):
        await ctx.send(f"링곤사전을 보니, 저의 아이큐는 {detect.getFullCount()}이라고 하네요!")
    
    @commands.command(name='배운거')
    async def RG_Studied(self, ctx: commands.Context):
        await embedManager.make(detect.getFullDetect(), ctx.channel)
    
    @commands.command(name='센서민감도')
    async def RG_Neungji(self, ctx: commands.Context):
        await ctx.send(f"링곤사전을 보니, 저의 센서민감도는 {detect.getPartCount()}이라고 하네요!")
    
    @commands.command(name='센서기록')
    async def RG_Sensor(self, ctx: commands.Context):
        await embedManager.make(detect.getPartCount(), ctx.channel)
