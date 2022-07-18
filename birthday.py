from typing import List

import discord
from discord.ext import commands, tasks

from util import utils
from util.baseDB import DB

class birthdayDB(DB):
    def __init__(self):
        super().__init__("DB/birthday.db")
    
    def getToday(self, now) -> List[int]:
        """get IDs for members whom birthday is today

        Parameters
        ----------
        * now: :class:`datetime.datetime`
            - datetime object that refers to now

        ."""
        date = now.strftime("%m/%d")
        return [
            val["ID"] for val in
            self._runSQL("SELECT ID FROM BIRTHDAY WHERE date=?", date)
        ]

db = birthdayDB()

class Birthday(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild: discord.Guild = None
        self.noticeCh: discord.TextChannel = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(758478112979288094)
        self.noticeCh = self.guild.get_channel(864518975253119007)
    
    @tasks.loop(hours = 1)
    async def birthdayCheckLoop(self):
        now = utils.now()
        if (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds >= 1*60*60: return
        
        members: List[discord.Member] = [self.guild.get_member(id) for id in db.getToday(now)]
        if len(members) == 0: return

        for member in members:
            member.add_roles(self.guild.get_role(952236601331810437))
        
        content  = f"오늘은 {'님, '.join(members)}님의 생일입니다! 모두 축하해주세요 :tada:"
        content += f"Today is {', '.join(members)}'s birthday! :partying_face:"
        await self.noticeCh.send(content)

def setup(bot):
    bot.add_cog(Birthday(bot))
