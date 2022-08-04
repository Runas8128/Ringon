from typing import List, Dict, Union
import asyncio
from datetime import timedelta
from time import time

import discord
from discord.ext import commands

from util import utils
from util.myBot import MyBot

T_Emoji = Union[discord.Emoji, discord.PartialEmoji, str]

class CogCheck(commands.Cog):    
    def __init__(self, bot: MyBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(self.bot.target_guild.id)

        self.IgnoreRole: List[discord.Role] = [
            guild.get_role(924315254098387024), # Guest of Honor
            guild.get_role(861883220722319391), # 군머
            guild.get_role(805451727859613707)  # 고3
        ] if not self.bot.is_testing else []

        self.Category: List[discord.CategoryChannel] = [
            self.bot.get_channel(891697283702345798), # LAB
            self.bot.get_channel(982903025322577940)  # Rating
        ] if not self.bot.is_testing else []

        self.NotNotifyRoom: discord.TextChannel = self.bot.get_channel(809342346466557952) \
            if not self.bot.is_testing else None
    
    @commands.command(name='인원점검')
    @commands.has_permissions(administrator=True)
    async def cmd_CheckMembers(self, ctx: commands.Context, tarMsgLink: str=''):
        if self.bot.is_testing:
            await ctx.reply("해당 명령어는 테스트 모드에서 사용 불가능한 명령어입니다.", mention_author=False)
        
        try:
            _, _, _, _, guildID, channelID, messageID = tarMsgLink.split('/')
            guild: discord.Guild = self.bot.get_guild(int(guildID))
            channel: discord.TextChannel = guild.get_channel(int(channelID))

            tarMsg = discord.Message = await channel.fetch_message(int(messageID))
        
        except discord.NotFound:
            await ctx.send(f"잘못된 메시지 링크입니다. `메시지 링크 복사` 버튼을 이용해 복사한 메시지 링크를 넣어주세요!")
        except ValueError:
            await ctx.send("잘못된 메시지 링크 형식입니다. `메시지 링크 복사` 버튼을 이용해 복사한 메시지 링크를 넣어주세요!")
        
        else:
            notMsg = await ctx.send("인원점검중...")
            userMap = await self.getMemberMap(ctx.guild, tarMsg.reactions, ['👍', '👎'])
            
            embed = discord.Embed(title="인원점검")
            for emoji in userMap.keys():
                embed.add_field(
                    name=emoji,
                    value=", ".join([user.mention for user in userMap[emoji]]) or "없음",
                    inline=False
                )
            await notMsg.edit(content="", embed=embed)
    
    @commands.command(name="채팅량검사")
    @commands.has_permissions(administrator=True)
    async def RG_CheckChatAmount(self, ctx: commands.Context):
        if self.bot.is_testing:
            await ctx.reply("해당 명령어는 테스트 모드에서 사용 불가능한 명령어입니다.", mention_author=False)

        tmp: discord.Message = await ctx.send(embed=discord.Embed(
            title="각 멤버의 채팅량을 불러오는 중입니다.",
            description=f"각 멤버에 대한 로그는 {self.NotNotifyRoom.mention}에서 봐주세요!"
        ))
        b = time()
        await asyncio.gather([
            self.getUserChatAmount(member) for member in ctx.guild.members
        ])
        e = time()
        await tmp.edit(embed=discord.Embed(
            title="전체 멤버의 채팅량을 불러왔습니다!",
            description=f"각 멤버의 채팅량은 {self.NotNotifyRoom.mention}을 참고해주세요!\n걸린 시간: {round(e - b, 2):.2f}초"
        ))

    async def getMemberMap(self, guild: discord.Guild, allReact: List[discord.Reaction], indiEmoji: List[T_Emoji]) -> Dict[T_Emoji, List[discord.Member]]:
        """|coro|

        This function makes emoji-member map.
        if member reacted with two or more emoji, then check first emoji only.

        Parameters
        ----------
        * guild: :class:`discord.Guild`
            - guild object for this context
        * allReact: :class:`List[discord.Reaction]`
            - all reaction of target message.
        * indiEmoji: :class:`List[discord.Emoji|discord.PartialEmoji|str]`
            - emoji which will be counted individually.
        
        Return value
        ------------
        * emoji - member list map, :class:`Dict[discord.Emoji|discord.PartialEmoji|str, List[discord.Member]]`
            - all member who reacted with emoji not in `indiEmoji` are stored in "그 외" key
            - all member who didn't reacted are stored in "반응 안함" key

        ."""

        userList: List[discord.Member] = [user for user in guild.members if not user.bot]

        userMap: Dict[T_Emoji, discord.Member] = { emoji : [] for emoji in indiEmoji }
        userMap['그 외'] = []
        userMap['반응 안함'] = []
        
        react: discord.Reaction
        for react in allReact:
            async for user in react.users():
                if user in userList:
                    user = userList.pop(userList.index(user))
                
                if react.emoji in indiEmoji:
                    userMap[react.emoji].append(user)
                else:
                    userMap['Other'].append(user)

        for ignoreRole in self.IgnoreRole:
            userList = [user for user in userList if ignoreRole not in user.roles]
        
        userMap['반응 안함'] = userList
        
        return userMap

    async def getUserChatAmount(self, member: discord.Member):
        """Count chat amount in `Lab` and `Rating` category and send count stack info to not-notifing-admin room.

        Parameters
        ----------
        * member: :class:`discord.Member`
            - Member object to get chat amount

        ."""
        noticeMessage: discord.Message = await self.NotNotifyRoom.send(f"{member.mention}님의 역할을 분석하는 중...")

        for role in self.IgnoreRole:
            if role in member.roles:
                await noticeMessage.edit(content=f"{member.mention}({role.name})님의 채팅량 검사를 건너뜁니다.")
                return
        
        await noticeMessage.edit(content=f"{member.mention}님의 채팅량을 세는 중...")
        
        def predicate(message: discord.Message):
            return message.author.id == member.id

        count = 0
        channel: discord.TextChannel
        for category in self.Category:
            for channel in category.channels:
                if not isinstance(channel, discord.TextChannel):
                    continue
                
                message: discord.Message
                async for _ in channel.history(after=utils.now()-timedelta(days=14), limit=50).find(predicate):
                    count += 1
                    if count >= 50:
                        await noticeMessage.edit(content=f"{member.mention}님의 채팅량: 50개 이상, 검사를 중단합니다.")
        await noticeMessage.edit(content=f"{member.mention}님의 채팅량은 {count}건입니다.")

async def setup(bot: MyBot):
    await bot.add_cog(CogCheck(bot), guild=bot.target_guild)
