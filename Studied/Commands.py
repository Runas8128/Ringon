#-*- coding: utf-8 -*-

from .Helper import *

class CogStudied(MyCog, name='전체감지'):
    """
    메시지의 전체를 감지하게 하는 명령어 카테고리입니다.
    """
    
    def __init__(self, bot):
        global studied
        studied = Studied()
        
        self.bot = bot
        
        self.AdminOnly = []
        self.OwnerOnly = []

        self.EngCmd = []
        self.KorCmd = [self.RG_Teach, self.RG_Forget, self.RG_Neungji, self.RG_Studied]

    @commands.command(
        name='배워',
        brief='링곤이에게 특정 문장을 배우게 합니다.',
        description='링곤이에게 특정 문장을 배우게 합니다. 나중에 정확히 그 문장이 챗에 올라오면 반응합니다.',
        usage='!배워 (배울 문장) = (반응할 문장)'
    )
    async def RG_Teach(self, ctx: commands.Context, *seq: str):
        seq: str = ' '.join(seq)
        if seq.count('=') != 1:
            await ctx.send('사용법: `!배워 __ = __`')
            return

        src, dst = seq.split('=')
        studied.add(src.strip(), dst.strip())
        await ctx.send(f'{src}는 {dst}라는걸 배웠어요!')

    @commands.command(
        name='잊어',
        brief='링곤이가 배운 특정 문장을 잊게 합니다.',
        description='링곤이가 배운 특정 문장을 잊게 합니다. 이후에 해당 문장에 반응하지 않습니다.',
        usage='!잊어 (배운 문장)'
    )
    async def RG_Forget(self, ctx: commands.Context, *src: str):
        s: str = ' '.join(src).strip()

        if s in studied.taughts:
            studied.rem(s)
            await ctx.send(f'{s}가 기억이 안날지도..?')
        else:
            await ctx.send('그래서 그게 뭐였죠..?')

    @commands.command(
        name='능지',
        brief='링곤이가 배운 총 문장의 개수를 보여줍니다.',
        description='링곤이가 배운 총 문장의 개수를 보여줍니다.',
        usage='!능지'
    )
    async def RG_Neungji(self, ctx: commands.Context):
        await ctx.send(f"링곤사전을 보니, 저의 아이큐는 {len(studied.taughts.keys())}이라고 하네요!")

    @commands.command(
        name='배운거',
        brief='링곤이가 배운 문장을 모두 알려줍니다.',
        description='링곤이가 배운 문장을 모두 알려줍니다. 10개씩 끊어서 보여주며, 이모지를 눌러서 페이지별로 이동이 가능합니다.',
        usage='!배운거'
    )
    async def RG_Studied(self, ctx: commands.Context):
        iq = len(studied.taughts)

        if iq == 0:
            studied.StudiedEmbedMsg = None
            await ctx.send('링곤이 멍청하당.. 헣허')

        else:
            studied.StudiedEmbedMsg = await ctx.send(embed=studied.Top())

            if iq > 10:
                await studied.StudiedEmbedMsg.add_reaction('🔼')
                await studied.StudiedEmbedMsg.add_reaction('🔽')
                
            if iq > 20:
                await studied.StudiedEmbedMsg.add_reaction('⏫')
                await studied.StudiedEmbedMsg.add_reaction('⏬')
