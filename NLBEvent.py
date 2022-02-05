from typing import Dict, Literal, Tuple

from Common import *

class CogNLB(MyCog, name='변경예약'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.AdminOnly = []
        self.OwnerOnly = [self.RG_Reserve]

        self.EngCmd = [self.RG_Reserve]
        self.KorCmd = [self.RG_Reserve]

        self.Notice: discord.TextChannel = None
        self.Guild: discord.Guild = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.ReserveEvent.is_running:
            self.ReserveEvent.start()
        self.Notice = self.bot.get_channel(864518975253119007)
        self.Guild = self.bot.get_guild(758478112979288094)

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

        if Type == '공지':
            content: str = ' '.join(content).replace('\\n', '\n')
            if content:
                d.append(('Notice', (' '.join(content)).replace('\\n', '\n')))
                await ctx.message.add_reaction("<:comfortable:781545336291197018>")
            else:
                await ctx.send("공지 내용을 작성해주세요")
        elif Type == '로고':
            atts: List[discord.Attachment] = ctx.message.attachments
            if atts:
                d.append(('Logo', await atts[0].read()))
                await ctx.message.add_reaction("<:comfortable:781545336291197018>")
            else:
                await ctx.send("로고 사진을 첨부해주세요")
        elif Type == '배너':
            atts: List[discord.Attachment] = ctx.message.attachments
            if atts:
                d.append(('Banner', await atts[0].read()))
                await ctx.message.add_reaction("<:comfortable:781545336291197018>")
            else:
                await ctx.send("배너 사진을 첨부해주세요")
        else:
            await ctx.send("사용법: !예약 [공지/로고/배너] ...")

    @tasks.loop(minutes=5)
    async def ReserveEvent(self, util: Dict[str, Union[discord.Guild, discord.TextChannel]]={}):
        # 자정에만 실행되게 함
        _now = now()
        delta = (_now - _now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        if not(0 <= delta and delta < 5 * 60): return

        T: Literal['Notice', 'Logo', 'Banner']
        C: Union[str, bytes]
        for T, C in db['EventQueue']: # Type, Content
            if T == 'Notice': await self.Notice.send(C)
            elif T == 'Logo': await self.Guild.edit(icon=C)
            elif T == 'Banner': await self.Guild.edit(banner=C)
                
        db['EventQueue'] = []

def setup(bot):
    bot.add_cog(CogNLB(bot))