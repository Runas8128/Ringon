from typing import List, Tuple

from Common import *
from Events import CogEvent

class CogOther(MyCog, name='기타'):
    """
    기타 링곤이의 명령어를 보여줍니다.
    관리자용 명령어가 다른 카테고리보다 많이 있으며,
    이 카테고리의 명령어는 자주 사용할 일이 없을것입니다. 아마도?
    """
    
    # __init__
    
    def __init__(self, bot):
        self.bot = bot
        
        self.AdminOnly = [self.RG_BlockWordAdd, self.RG_BlockWordRem, self.RG_PrizeSet, self.RG_Reserve]
        self.OwnerOnly = []
        
        self.EngCmd = [self.RG_Ping_EN]
        self.KorCmd = [
            self.RG_BlockWordAdd, self.RG_BlockWordRem, self.RG_BlockWordView,
            self.RG_MaxPrize, self.RG_Prize, self.RG_PrizeSet,
            self.RG_Ping_KR, self.ShowCode, self.RG_Reserve
        ]
    
    # Block Words
    
    @commands.command(
        name='금칙어추가',
        brief='금칙어를 추가합니다. 관리자용 명령어입니다.',
        description='금칙어를 추가합니다. 금칙어는 공백을 포함할 수 있습니다. 관리자용 명령어입니다.',
        usage='!금칙어추가 (금칙어)'
    )
    @commands.has_permissions(administrator=True)
    async def RG_BlockWordAdd(self, ctx: commands.Context, *block: str):
        block: str = ' '.join(block)
        
        if block not in db['WordBlock']:
            db['WordBlock'].insert(len(db['WordBlock']), block) # same with list.append(Any)
            await ctx.send(f'{block} 단어를 금칙어로 설정했어요!')
        else:
            await ctx.send('이미 금칙어로 정해진 단어입니다!')
    
    @commands.command(
        name='금칙어제거',
        brief='금칙어를 제거합니다. 관리자용 명령어입니다.',
        description='금칙어를 제거합니다. 금칙어는 공백을 포함할 수 있으며, 없는 금칙어는 제거되지 않습니다. 관리자용 명령어입니다.',
        usage='!금칙어제거 (금칙어)'
    )
    @commands.has_permissions(administrator=True)
    async def RG_BlockWordRem(self, ctx: commands.Context, *block: str):
        block: str = ' '.join(block)
        
        if block in db['WordBlock']:
            db['WordBlock'].remove(block)
            await ctx.send(f'{block} 단어를 금칙어에서 제외했어요!')
        else:
            await ctx.send('금칙어가 아닌 단어입니다!')
    
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
    
    # Prizes
    
    @commands.command(
        name='상금',
        brief='우승자와 준우승자의 상금 금액을 뽑아줍니다.',
        description='우승자와 준우승자의 상금 금액을 뽑아줍니다. 준우승자의 상금은 우승자의 상금보다 항상 작습니다.',
        usage='!상금'
    )
    async def RG_Prize(self, ctx: commands.Context):
        w = int(random() * db['maxPrize'] + 1)
        pw = int(random() * (w - 1) + 1)
        
        await ctx.send(f'우승자 상금은 {w}만원, 준우승자 상금은 {pw}만원이 좋겠어요!')
    
    @commands.command(
        name='최대상금',
        brief='우승자의 상금으로 나올 수 있는 최댓값을 보여줍니다.',
        description='우승자의 상금으로 나올 수 있는 최댓값을 보여줍니다.',
        usage='!최대상금'
    )
    async def RG_MaxPrize(self, ctx: commands.Context):
        await ctx.send(f"현재 최대상금은 {db['maxPrize']}만원이에요!")
    
    @commands.command(
        name='상금지정',
        brief='우승자의 최대 상금을 지정합니다. 관리자용 명령어입니다.',
        description='우승자의 최대 상금을 지정합니다. 관리자용 명령어입니다.',
        usage='!상금지정 (새 최대 상금 - 정수)'
    )
    @commands.has_permissions(administrator=True)
    async def RG_PrizeSet(self, ctx: commands.Context, new: int=0):
        if new > 1:
            db['maxPrize'] = new
            await ctx.send(f'우승자 상금의 최대치를 {new}만원으로 바꿨어요!')
        elif new == 0:
            await ctx.send("사용법: !상금지정 (새 상금: 정수)")
        else:
            await ctx.send(f'우승자가 {new}만원 가져가면 준우승자는요..?')
    
    # PING Command
    
    @commands.command(
        name='지연시간',
        brief='현재 봇이 메시지를 보내는데 걸린 시간을 측정합니다.',
        description='현재 봇이 메시지를 보내는데 걸린 시간을 측정합니다. 평소에는 대략 150~250ms 정도입니다.',
        usage='!지연시간'
    )
    async def RG_Ping_KR(self, ctx: commands.Context):
        tB = time()
        msg = await ctx.send('지연시간 계산중...')
        tE = time()
        await msg.edit(content=f'현재 지연시간은 {round((tE - tB) * 1000, 2)}ms 입니다!')
    
    @commands.command(
        name='latency', aliases=['delay'],
        brief='time how long takes for the bot to send message',
        description='time how long takes for the bot to send message. It usually takes about 150~250ms.',
        usage='!latency'
    )
    async def RG_Ping_EN(self, ctx: commands.Context):
        tB = time()
        msg = await ctx.send('Getting delay...')
        tE = time()
        await msg.edit(content=f'Now delay is {round((tE - tB) * 1000, 2)}ms!')
    
    # Show This Repl
    
    @commands.command(
        name='코드보기',
        brief='링곤이의 코드를 볼 수 있습니다.',
        description='링곤이의 코드를 볼 수 있습니다. ~~쓸 사람이 얼마나 될지~~',
        usage='!코드보기'
    )
    async def ShowCode(self, ctx: commands.Context):
        await ctx.send('https://github.com/Runas8128/Ringon')
    
    # Reserve Changing Server
    
    @commands.command(
        name='예약',
        brief='공지를 쓰거나 로고/배너 수정을 예약할 수 있습니다. 관리자용 명령어입니다.',
        description='공지를 쓰거나 로고/배너 수정을 예약할 수 있습니다. 다음날 오전 12시(00:00)에 해당 예약을 실행합니다. 관리자용 명령어입니다.',
        usage='!예약 [공지/로고/배너]'
    )
    @commands.has_permissions(administrator=True)
    async def RG_Reserve(self, ctx: commands.Context, Type: str='', *content: str):
        d: List[Tuple[str, Union[str, bytes]]] = db['EventQueue']
        content: str = ' '.join(content).replace('\\n', '\n')
        atts: List[discord.Attachment] = ctx.message.attachments
        
        if Type == '공지':
            if content:
                d.append(('Notice', (' '.join(content)).replace('\\n', '\n')))
                await ctx.message.add_reaction("<:comfortable:781545336291197018>")
            else:
                await ctx.send("공지 내용을 작성해주세요")
        elif Type == '로고':
            if atts:
                d.append(('Logo', await atts[0].read()))
                await ctx.message.add_reaction("<:comfortable:781545336291197018>")
            else:
                await ctx.send("로고 사진을 첨부해주세요")
        elif Type == '배너':
            if atts:
                d.append(('Banner', await atts[0].read()))
                await ctx.message.add_reaction("<:comfortable:781545336291197018>")
            else:
                await ctx.send("배너 사진을 첨부해주세요")
        else:
            await ctx.send("사용법: !예약 [공지/로고/배너] ...")

def setup(bot):
    bot.add_cog(CogOther(bot))
