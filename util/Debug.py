from typing import List

import discord
from discord.ext import commands

class CogDebug(commands.Cog):    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.AdminOnly = [self.cmd_CheckMembers]
        self.OwnerOnly = []
        
        self.EngCmd = []
        self.KorCmd = [self.cmd_CheckMembers]
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(758478112979288094)
        self.bugReportChannel: discord.TextChannel = self.bot.get_channel(884356850248724490)
        self.ServerNotice: discord.TextChannel = self.bot.get_channel(765759817662857256)
        
        self.IgnoreRole: List[discord.Role] = [
            self.guild.get_role(924315254098387024), # Guest of Honor
            self.guild.get_role(861883220722319391), # 군머
            self.guild.get_role(805451727859613707)  # 고3
        ]
    
    @commands.command(name='인원점검')
    @commands.has_permissions(administrator=True)
    async def cmd_CheckMembers(self, ctx: commands.Context, sted: str = '끝', tarMsgID: int = 0):
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
                tarMsg: discord.Message = await self.ServerNotice.fetch_message(tarMsgID)
            except discord.NotFound:
                await ctx.send(f"잘못된 메시지 아이디 입니다. {self.ServerNotice.mention} 채널의 글인지 확인해주세요!")
            else:
                notMsg = await ctx.send("인원점검중...")
                userList: List[discord.Member] = [user for user in ctx.guild.members if not user.bot]
                
                for ignoreRole in self.IgnoreRole:
                    userList = [user for user in userList if ignoreRole not in user.roles]
                
                upUserList: List[discord.Member] = []
                downUserList: List[discord.Member] = []
                otherUserList: List[discord.Member] = []
                
                react: discord.Reaction
                for react in tarMsg.reactions:
                    async for user in react.users():
                        if user in userList:
                            user = userList.pop(userList.index(user))
                            if react.emoji == '👍':
                                upUserList.append(user)
                            if react.emoji == '👎':
                                downUserList.append(user)
                            else:
                                otherUserList.append(user)
                
                embed = discord.Embed(title="인원점검")
                
                embed.add_field(
                    name='👍 반응',
                    value=", ".join([user.mention for user in upUserList]) or "없음"
                )
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