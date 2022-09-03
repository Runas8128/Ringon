from typing import List, Dict, Union

import discord
from discord import app_commands
from discord.ext import commands

from ringon import Ringon

T_Emoji = Union[discord.Emoji, discord.PartialEmoji, str]

class CogCheck(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot

        self.ignore_role: List[discord.Role] = []

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(self.bot.target_guild.id)

        if not self.bot.is_testing:
            self.ignore_role = [
                guild.get_role(924315254098387024), # Guest of Honor
                guild.get_role(861883220722319391), # 군머
                guild.get_role(805451727859613707)  # 고3
            ]

    @app_commands.command(name="인원점검")
    @app_commands.default_permissions(administrator=True)
    async def cmd_CheckMembers(
        self, interaction: discord.Interaction,
        tarMsgLink: str=''
    ):
        if self.bot.is_testing:
            return await interaction.response.send_message(
                "해당 명령어는 테스트 모드에서 사용 불가능한 명령어입니다."
            )

        try:
            _, _, _, _, guildID, channelID, messageID = tarMsgLink.split('/')
            guild: discord.Guild = self.bot.get_guild(int(guildID))
            channel: discord.TextChannel = guild.get_channel(int(channelID))

            tarMsg = discord.Message = await channel.fetch_message(int(messageID))

        except discord.NotFound:
            return await interaction.response.send_message(
                "잘못된 메시지 링크입니다. "
                "`메시지 링크 복사` 버튼을 이용해 복사한 메시지 링크를 넣어주세요!"
            )
        except ValueError:
            return await interaction.response.send_message(
                "잘못된 메시지 링크 형식입니다. "
                "`메시지 링크 복사` 버튼을 이용해 복사한 메시지 링크를 넣어주세요!"
            )

        await interaction.response.defer()

        notMsg = await interaction.followup.send("인원점검중...")
        userMap = await self.getMemberMap(
            interaction.guild,
            tarMsg.reactions,
            ['👍', '👎']
        )

        embed = discord.Embed(title="인원점검")
        for emoji, users in userMap.items():
            embed.add_field(
                name=emoji,
                value=", ".join([user.mention for user in users]) or "없음",
                inline=False
            )
        await interaction.followup.edit_message(notMsg.id, content="", embed=embed)

    async def getMemberMap(
        self,
        guild: discord.Guild,
        allReact: List[discord.Reaction],
        indiEmoji: List[T_Emoji]
    ) -> Dict[T_Emoji, List[discord.Member]]:
        """Makes emoji-member map.
        If member reacted with two or more emoji, then check first emoji only.
        This function is coroutine.

        ### Args ::
            guild (discord.Guild):
                guild object for this context
            allReact (List[discord.Reaction]):
                all reaction of target message.
            indiEmoji (List[TEmoji]):
                emoji which will be counted individually.

        ### Returns ::
            dict[T_Emoji, List[discord.Member]]: emoji - member list map
                all member who reacted with emoji not in `indiEmoji` are stored in "그 외" key
                all member who didn't reacted are stored in "반응 안함" key
        """

        userList: List[discord.Member] = [
            user
            for user in guild.members
            if not user.bot
        ]

        userMap: Dict[T_Emoji, discord.Member] = {
            emoji : []
            for emoji in indiEmoji
        }
        userMap['그 외'] = []

        react: discord.Reaction
        for react in allReact:
            async for user in react.users():
                if user in userList:
                    user = userList.pop(userList.index(user))

                if react.emoji in indiEmoji:
                    userMap[react.emoji].append(user)
                else:
                    userMap['그 외'].append(user)

        userMap['반응 안함'] = [
            user
            for user in userList
            if any(
                ignore_role not in user.roles
                for ignore_role in self.ignore_role
            )
        ]

        return userMap

async def setup(bot: Ringon):
    await bot.add_cog(CogCheck(bot), guild=bot.target_guild)
