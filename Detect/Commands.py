#-*- coding: utf-8 -*-

from .Helper import *

class CogDetect(MyCog, name='일부감지'):
    """
    메시지의 일부를 감지하게 하는 명령어 카테고리입니다.
    """
    
    # ----- __init__ -----
    
    def __init__(self, bot):
        self.bot = bot
        
        self.AdminOnly = []
        self.OwnerOnly = []
        
        self.EngCmd = []
        self.KorCmd = [self.RG_Neungji, self.RG_Sensor]
    
    # ----- Commands -----
    
    @commands.command(name='감지')
    async def RG_Detect(self, ctx: commands.Context):
        await ctx.send("이 명령어는 더 이상 작동하지 않습니다. 관리자분들께 직접 건의해주세요!")
    
    @commands.command(name='감지취소')
    async def RG_NotDetect(self, ctx: commands.Context):
        await ctx.send("이 명령어는 더 이상 작동하지 않습니다. 관리자분들께 직접 건의해주세요!")
    
    @commands.command(
        name='센서민감도',
        brief='링곤이가 감지할 총 문장의 개수를 보여줍니다.',
        description='링곤이가 감지할 총 문장의 개수를 보여줍니다.',
        usage='!센서민감도'
    )
    async def RG_Neungji(self, ctx: commands.Context):
        await ctx.send(f"링곤사전을 보니, 저의 센서민감도는 {len(detect.detects.keys())}이라고 하네요!")
    
    @commands.command(
        name='센서기록',
        brief='링곤이가 감지할 문장을 모두 알려줍니다.',
        description='링곤이가 감지할 문장을 모두 알려줍니다. 10개씩 끊어서 보여주며, 이모지를 눌러서 페이지별로 이동이 가능합니다.',
        usage='!센서기록'
    )
    async def RG_Sensor(self, ctx: commands.Context):
        iq = len(detect.detects)
        
        if iq == 0:
            detect.detectEmbedMsg = None
            await ctx.send('링곤이 멍청하당.. 헣허')
        
        else:
            detect.detectEmbedMsg = await ctx.send(embed=detect.Top())
            
            if iq > 10:
                await detect.detectEmbedMsg.add_reaction('🔼')
                await detect.detectEmbedMsg.add_reaction('🔽')
            
            if iq > 20:
                await detect.detectEmbedMsg.add_reaction('⏫')
                await detect.detectEmbedMsg.add_reaction('⏬')
