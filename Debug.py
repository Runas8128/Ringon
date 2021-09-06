from Common import *

class CogDebug(MyCog, name='디버그'):
    """
    디버그용 커맨드 그룹입니다.
    개발자 전용 커맨드 그룹이며, 굳이 써봐야 볼 내용도 많이 없습니다.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.AdminOnly = []
        self.OwnerOnly = [self.cmd_ShowDB, self.cmd_ShowDBKey]

        self.EngCmd = [self.cmd_ShowDB, self.cmd_ShowDBKey]
        self.KorCmd = [self.cmd_ShowDB, self.cmd_ShowDBKey, self.cmd_IssueError]

        self.bugReportChannel: discord.TextChannel = None
    
    @commands.command(
        name='show',
        brief='DB를 보여줍니다. 디버그용 명령어입니다.',
        description='DB의 내용을 보여줍니다. 디버그용 명령어로, 거의 쓸 일이 없는 명령어입니다.',
        usage='!show (키 나열)'
    )
    @commands.is_owner()
    async def cmd_ShowDB(self, ctx: commands.Context, mainKey: str = 'None', *keys: str):
        if mainKey in db.keys():
            d = db[mainKey]
            for key in keys:
                if isinstance(d, dict) and (key in d.keys()):
                    d = d[key]
                else:
                    await ctx.send(f'{key} not in {d}')
                    return
            await ctx.send(d)
        else:
            await ctx.send(f'{mainKey} not in {db.keys()}')

    @commands.command(
        name='showKey',
        brief='DB의 키를 보여줍니다. 디버그용 명령어입니다.',
        description='DB의 키를 보여줍니다. 디버그용 명령어로, 거의 쓸 일이 없는 명령어입니다.',
        usage='!showKey (키 나열)'
    )
    @commands.is_owner()
    async def cmd_ShowDBKey(self, ctx: commands.Context, mainKey: str = None, *keys: str):
        if mainKey in db.keys():
            d = db[mainKey]
            for key in keys:
                if isinstance(d, dict) and (key in d.keys()):
                    d = d[key]
                else:
                    await ctx.send(f'{key} not in {d}')
                    return
            if isinstance(d, dict):
                await ctx.send(d.keys())
            else:
                await ctx.send(d)
        elif mainKey == None:
            await ctx.send(db.keys())
        else:
            await ctx.send(f'{mainKey} not in {db.keys()}')

    @commands.command(
        name='버그',
        brief='버그를 제보합니다.',
        description='개발자가 쉬는동안 가끔 하고싶을때 고칠 버그를 알려줍니다.',
        usage='!버그 (제보할 내용)'
    )
    async def cmd_IssueError(self, ctx: commands.Context, *content: str):
        if not self.bugReportChannel:
            self.bugReportChannel = self.bot.get_channel(884356850248724490)
        await self.bugReportChannel.send(' '.join(content))
        await ctx.send("버그를 제보했어요! 이미 제보된 내용일지는 저도 모르겠네요... 가끔 잠수함 패치로 고쳐질지도..?")

def setup(bot):
    bot.add_cog(CogDebug(bot))