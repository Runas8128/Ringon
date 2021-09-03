#-*- coding: utf-8 -*-

from .Helper import *

class CogDetect(MyCog, name='일부감지'):
    """
    메시지의 일부를 감지하게 하는 명령어 카테고리입니다.
    """
    
    # ----- __init__ -----
    
    def __init__(self, bot):
        global detect
        detect = Detect()
        
        self.bot = bot
        
        self.AdminOnly = []
        self.OwnerOnly = []

        self.EngCmd = []
        self.KorCmd = [self.RG_Detect, self.RG_Neungji, self.RG_NotDetect, self.RG_Sensor]
    
    # ----- Commands -----

    @commands.command(
        name='감지',
        brief='링곤이에게 특정 문장을 감지하게 합니다.',
        description='링곤이에게 특정 문장을 감지하게 합니다. 나중에 그 문장이 포함된 말이 챗에 올라오면 반응합니다.',
        usage='!감지 (배울 문장) = (반응할 문장)'
    )
    async def RG_Detect(ctx: commands.Context, *seq: str):
        seq = ' '.join(seq)

        if seq.count('=') != 1:
            await ctx.send('사용법: `!감지 __ = __`')
        else:
            src, dst = seq.split('=')
            detect.add(src.strip(), dst.strip())
            detect.stop()
            await ctx.send(f'{src}를 감지하면 {dst}라고 할게요!')

    @commands.command(
        name='감지취소',
        brief='링곤이가 감지할 특정 문장을 잊게 합니다.',
        description='링곤이가 감지할 특정 문장을 잊게 합니다. 이후에 해당 문장에 반응하지 않습니다.',
        usage='!감지취소 (배운 문장)'
    )
    async def RG_NotDetect(ctx: commands.Context, *tar: str):
        tar: str = ' '.join(tar)
        
        if tar in detect.detects.keys():
            detect.rem(tar)
            await ctx.send(f'앞으로 {tar}에 반응하지 않을게요!')
        else:
            await ctx.send('원래 있지도 않았어요 그런거..')

    @commands.command(
        name='센서민감도',
        brief='링곤이가 감지할 총 문장의 개수를 보여줍니다.',
        description='링곤이가 감지할 총 문장의 개수를 보여줍니다.',
        usage='!센서민감도'
    )
    async def RG_Neungji(ctx: commands.Context):
        await ctx.send(f"링곤사전을 보니, 저의 센서민감도는 {len(detect.detects.keys())}이라고 하네요!")

    @commands.command(
        name='센서기록',
        brief='링곤이가 감지할 문장을 모두 알려줍니다.',
        description='링곤이가 감지할 문장을 모두 알려줍니다. 10개씩 끊어서 보여주며, 이모지를 눌러서 페이지별로 이동이 가능합니다.',
        usage='!센서기록'
    )
    async def RG_Sensor(ctx: commands.Context):
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
