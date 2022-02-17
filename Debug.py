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
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(783257655388012584) #758478112979288094
        self.bugReportChannel: discord.TextChannel = self.bot.get_channel(884356850248724490)
        self.MainNoticeChannel: discord.TextChannel = self.bot.get_channel(783257655388012587) #864518975253119007

        self.IgnoreRole: List[discord.Role] = [
            self.guild.get_role(924315254098387024), # Guest of Honor
            self.guild.get_role(861883220722319391), # 군머
            self.guild.get_role(805451727859613707)  # 고3
        ]
    
    @commands.command(
        name='showAll'
    )
    async def cmd_ShowAllDB(self, ctx: commands.Context):
        print(db)
    
    @commands.command(
        name='show',
        brief='DB를 보여줍니다. 디버그용 명령어입니다.',
        description='DB의 내용을 보여줍니다. 디버그용 명령어로, 거의 쓸 일이 없는 명령어입니다.',
        usage='!show (키 나열)'
    )
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
        await self.bugReportChannel.send(' '.join(content))
        await ctx.send("버그를 제보했어요! 이미 제보된 내용일지는 저도 모르겠네요... 가끔 잠수함 패치로 고쳐질지도..?")
    
    @commands.command(
        name='인원1점검',
        brief='인원점검 공지를 올립니다. 관리자 권한입니다.',
        description='인원점검 공지를 올립니다. 관리자 권한입니다.',
        usage='!인원점검'
    )
    @commands.has_permissions(administrator=True)
    async def cmd_CheckMembers(self, ctx: commands.Context, sted: str = '없음', tarMsgID: int = 0):
        if sted == '시작':
            """try:
                def check(msg: discord.Message):
                    return msg.channel == ctx.channel and msg.content == "확인"

                embed = discord.Embed(
                    title="※ 경고 ※",
                    description="해당 명령어는 공지에 쓰는 에블핑을 포함하고 있습니다.\n사용하시려면 `확인`을 30초 안에 입력해주세요."
                )
                await ctx.send(embed=embed)
                await self.bot.wait_for('message', timeout=30, check=check)
            except asyncio.TimeoutError:
                await ctx.send("명령어 실행을 취소합니다.")
            else:
                tarMsg = await ctx.send("에블핑 뺀 인원점검 메시지")
                await ctx.send(f'이번 인원점검 메시지 아이디는 {tarMsg.id}입니다.')"""
            await ctx.send("아직 추가되지 않았습니다.")

        elif sted == '끝' and tarMsgID != 0:
            try:
                tarMsg: discord.Message = await self.MainNoticeChannel.fetch_message(tarMsgID)
            except discord.NotFound:
                await ctx.send("잘못된 메시지 아이디 입니다.")
            else:
                notMsg = await ctx.send("인원점검중...")
                userList: List[discord.Member] = [user for user in ctx.guild.members if not user.bot]

                for ignoreRole in self.IgnoreRole:
                    userList = [user for user in userList if ignoreRole not in user.roles]

                downUserList: List[discord.Member] = []
                otherUserList: List[discord.Member] = []

                react: discord.Reaction
                for react in tarMsg.reactions:
                    async for user in react.users():
                        if user in userList:
                            user = userList.pop(userList.index(user))
                            if react.emoji == '👎':
                                downUserList.append(user)
                            else:
                                otherUserList.append(user)

                embed = discord.Embed(title="인원점검")

                embed.add_field(
                    name="👎 반응",
                    value=", ".join([user.mention for user in downUserList]) or "없음"
                )
                embed.add_field(
                    name="그 외",
                    value=", ".join([user.mention for user in otherUserList]) or "없음"
                )
                embed.add_field(
                    name="반응 안함",
                    value=", ".join([user.mention for user in userList]) or "없음"
                )
                
                await notMsg.edit(content="", embed=embed)
        else:
            await ctx.send("사용법: `!인원점검 시작` / `!인원점검 끝 (메시지 아이디)`")

def setup(bot):
    bot.add_cog(CogDebug(bot))