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
        self.MainNoticeChannel: discord.TextChannel = None
    
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
    
    @commands.command(
        name='인원점검',
        brief='인원점검 공지를 올립니다. 관리자 권한입니다.',
        description='인원점검 공지를 올립니다. 관리자 권한입니다.',
        usage='!인원점검'
    )
    @commands.has_permissions(administrator=True)
    async def cmd_CheckMembers(self, ctx: commands.Context, sted: str = '시작', tarMsgID: int = 0):
        MainNoticeChannel = self.bot.get_channel(783257655388012587)

        if sted == '시작':
            tarMsg = await MainNoticeChannel.send("@everyone 인원점검을 시작합니다. 이 메시지에 아무 반응이나 달아주시면 되겠습니다.")
            await ctx.send(f'이번 인원점검 메시지 아이디는 {tarMsg.id}입니다.')

        elif sted == '끝' and tarMsgID != 0:
            try:
                tarMsg = await MainNoticeChannel.fetch_message(tarMsgID)
            except discord.NotFound:
                await ctx.send("잘못된 메시지 아이디 입니다.")
            else:
                userList: List[discord.Member] = [user for user in ctx.guild.members if not user.bot]
                print('full list:', userList)

                react: discord.Reaction
                for react in tarMsg.reactions:
                    async for user in react.users():
                        if user in userList:
                            userList.pop(userList.index(user))
                            print('pop!', user)

                if len(userList) == 0:
                    await ctx.send("모든 분이 이번 인원 점검에 참여해주셨습니다!")
                else:
                    await ctx.send(
                        "이번 인원점검에 참여하지 않은 분들입니다.\n" + \
                            ', '.join([user.mention for user in userList])
                    )
        else:
            await ctx.send("사용법: `!인원점검 시작` / `!인원점검 끝 (메시지 아이디)`")

def setup(bot):
    bot.add_cog(CogDebug(bot))