from typing  import List, Union, Tuple
from time    import time
from asyncio import TimeoutError
from random  import random

import discord
from discord.ext import commands

from util.myBot import MyBot

class CogOther(commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
    
    @commands.command(
        name='금칙어',
        brief='현재 등록된 금칙어를 제공합니다.',
        description='현재 등록된 금칙어를 제공합니다. 금칙어는 자주 쓰이지 않고, ~~아마도~~봐서 좋을게 없기 때문에 5초 후 삭제됩니다.',
        usage='!금칙어'
    )
    async def RG_BlockWordView(self, ctx: commands.Context):
        s = '\n'.join(db['WordBlock'])
        await ctx.send(
            f"현재 금칙어 목록(5초 후 삭제됩니다.)\n```{s}```",
            delete_after=5
        )
    
    @commands.command(name='지연시간')
    async def RG_Ping_KR(self, ctx: commands.Context):
        tB = time()
        msg = await ctx.send('지연시간 계산중...')
        tE = time()
        await msg.edit(content=f'현재 지연시간은 {round((tE - tB) * 1000, 2)}ms 입니다!')
    
    @commands.command(name='latency', aliases=['delay'])
    async def RG_Ping_EN(self, ctx: commands.Context):
        tB = time()
        msg = await ctx.send('Getting delay...')
        tE = time()
        await msg.edit(content=f'Now delay is {round((tE - tB) * 1000, 2)}ms!')

async def setup(bot: MyBot):
    bot.add_cog(CogOther(bot), bot.target_guild)
