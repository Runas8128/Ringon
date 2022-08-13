from typing import List

import discord
from discord.ext import commands, tasks

from util.utils import util
from util.birthday import birthdayDB
from util.myBot import MyBot

class Birthday(commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(self.bot.target_guild.id)

        self.noticeCh: discord.TextChannel = self.guild.get_channel(
            823359663973072960 if self.bot.is_testing else 864518975253119007
        ) 
        self.birthdayRole: discord.Role = self.guild.get_role(
            854505668785602561 if self.bot.is_testing else 952236601331810437
        )
    
    @tasks.loop(hours = 1)
    async def birthdayCheckLoop(self):
        now = util.now()
        if (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds >= 1*60*60: return
        
        members: List[discord.Member] = [self.guild.get_member(id) for id in birthdayDB.getToday(now)]
        if len(members) == 0: return

        mentions = [member.mention for member in members]
        for member in members: member.add_roles(self.birthdayRole)
        
        content  = f"오늘은 {'님, '.join(mentions)}님의 생일입니다! 모두 축하해주세요 :tada:"
        content += f"Today is {', '.join(mentions)}'s birthday! :partying_face:"
        await self.noticeCh.send(content)

async def setup(bot: MyBot):
    await bot.add_cog(Birthday(bot), guild=bot.target_guild)
