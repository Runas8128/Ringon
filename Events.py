from typing import Dict, Literal
from traceback import format_exc

from Common import *

from Studied.Helper import studied
from Detect.Helper  import detect

class CogEvent(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def defaultError(self, ctx: commands.Context):
        for ss in format_exc().split('\n\n'):
            await self.bot.get_channel(863719856061939723).send(ss)
        await ctx.send("잠시 오류가 나서, 개발자에게 버그 리포트를 작성해줬어요! 곧 고칠 예정이니 잠시만 기다려주세요 :)")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.ReserveEvent.is_running():
            self.ReserveEvent.start()
            await self.bot.change_presence(activity=discord.Game("덱, 프로필, 전적을 관리"))
            print("Ringonbot ON")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        msg = message.content
        ch  = message.channel

        if not msg.startswith('!금칙어'):
            block: str
            for block in db['WordBlock']:
                if block in msg:
                    await ch.send(f'금칙어 {block[0]}읍읍이 포함되었습니다', delete_after=5)
                    await message.delete()
                    return

        if msg in studied.taughts:
            await message.channel.trigger_typing()
            await ch.send(studied.get(msg))
            
        else:
            # Detect
            if detect._stop:
                detect.start()
                return
                
            detect.start()
            for dtt in detect.detects:
                if dtt in msg:
                    await message.channel.trigger_typing()
                    await ch.send(detect.detects[dtt])

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return

        _id = reaction.message.id
            
        if studied.StudiedEmbedMsg and _id == studied.StudiedEmbedMsg.id:
            if reaction.emoji == '⏫':
                await studied.StudiedEmbedMsg.edit(embed=studied.Top())
            elif reaction.emoji == '🔼':
                await studied.StudiedEmbedMsg.edit(embed=studied.Up())
            elif reaction.emoji == '🔽':
                await studied.StudiedEmbedMsg.edit(embed=studied.Down())
            elif reaction.emoji == '⏬':
                await studied.StudiedEmbedMsg.edit(embed=studied.Bottom())

        elif detect.detectEmbedMsg and _id == detect.detectEmbedMsg.id:
            if reaction.emoji == '⏫':
                await detect.detectEmbedMsg.edit(embed=detect.Top())
            elif reaction.emoji == '🔼':
                await detect.detectEmbedMsg.edit(embed=detect.Up())
            elif reaction.emoji == '🔽':
                await detect.detectEmbedMsg.edit(embed=detect.Down())
            elif reaction.emoji == '⏬':
                await detect.detectEmbedMsg.edit(embed=detect.Bottom())

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("관리자 전용 명령어입니다! It's only for Admin")
        
        elif isinstance(error, commands.NotOwner):
            await ctx.send("개발자 전용 명령어입니다! It's only for Bot owner")
        
        elif isinstance(error, commands.errors.UserNotFound):
            await ctx.send("유저는 멘션이나 ID복사로 전달해주세요! Please send me it with mention or id")
        
        elif isinstance(error, discord.errors.HTTPException):
            if error.code not in [429]:   # Too Many Requests
                await self.defaultError(ctx)

        else:
            await self.defaultError(ctx)

    @tasks.loop(minutes=5)
    async def ReserveEvent(self, util: Dict[str, Union[discord.Guild, discord.TextChannel]]={}):
        _now = now()
        delta = (_now - _now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        if not(0 <= delta and delta < 5 * 60):
            return

        T: Literal['Notice', 'Logo', 'Banner']
        C: Union[str, bytes]
        for T, C in db['EventQueue']: # Type, Content
            if T == 'Notice':
                if 'Notice' not in util.keys():
                    util['Notice'] = self.bot.get_channel(864518975253119007)
                await util['Notice'].send(C)
            elif T == 'Logo':
                if 'Guild' not in util.keys():
                    util['Guild'] = self.bot.get_guild(758478112979288094)
                await util['Guild'].edit(icon=C)
            elif T == 'Banner':
                if 'Guild' not in util.keys():
                    util['Guild'] = self.bot.get_guild(758478112979288094)
                await util['Guild'].edit(banner=C)
                
        db['EventQueue'] = []

def setup(bot):
    bot.add_cog(CogEvent(bot))