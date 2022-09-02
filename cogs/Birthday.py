from typing import List

import discord
from discord.ext import commands, tasks

from util.utils import util
from util.birthday import birthdayDB
from ringon import Ringon

class Birthday(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot

        self.guild: discord.Guild = None
        self.notice_channel: discord.TextChannel = None
        self.birthday_role: discord.Role = None

        birthdayDB.load()

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(self.bot.target_guild.id)

        if self.bot.is_testing:
            self.notice_channel = self.guild.get_channel(823359663973072960)
            self.birthday_role = self.guild.get_role(854505668785602561)
        else:
            self.notice_channel = self.guild.get_channel(864518975253119007)
            self.birthday_role = self.guild.get_role(952236601331810437)

    @tasks.loop(hours = 1)
    async def birthdayCheckLoop(self):
        now = util.now
        if (
            now - now.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds() >= 1*60*60:
            return

        members: List[discord.Member] = [
            self.guild.get_member(id)
            for id in birthdayDB.get_today(now)
        ]
        if len(members) == 0:
            return

        mentions = [member.mention for member in members]
        for member in members:
            member.add_roles(self.birthday_role)

        content  = f"오늘은 {'님, '.join(mentions)}님의 생일입니다! 모두 축하해주세요 :tada:"
        content += f"Today is {', '.join(mentions)}'s birthday! :partying_face:"
        await self.notice_channel.send(content)

async def setup(bot: Ringon):
    await bot.add_cog(Birthday(bot), guild=bot.target_guild)
