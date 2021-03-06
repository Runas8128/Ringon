import io

from Common import *

class CogEvent(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ErrLogCh: discord.TextChannel = None
        self.AdminCh: discord.TextChannel = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game("덱, 프로필, 전적을 관리")
        )
        
        self.ErrLogCh = self.bot.get_channel(863719856061939723) # 783539105374928986
        self.AdminCh = self.bot.get_channel(783539105374928986)
        
        print("Ringonbot ON")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        msg = message.content
        ch  = message.channel
        atr = message.author
        
        if isinstance(ch, discord.channel.DMChannel):
            att = message.attachments
            if len(att) == 0:
                await self.AdminCh.send(f"{atr.mention}님의 DM입니다!\n" + msg)
            elif len(att) == 1:
                file = discord.File(io.BytesIO(await att[0].read()), att[0].filename)
                await self.AdminCh.send(f"{atr.mention}님의 DM입니다!\n" + msg, file=file)
            else:
                files = [discord.File(io.BytesIO(await att[idx].read()), att[idx].filename) for idx in range(len(att))]
                await self.AdminCh.send(f"{atr.mention}님의 DM입니다!\n" + msg, files=files)
            return
        
        if not msg.startswith('!금칙어'):
            block: str
            for block in db['WordBlock']:
                if block in msg:
                    await ch.send(f'금칙어 {block[0]}읍읍이 포함되었습니다', delete_after=5)
                    await message.delete()
                    return
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("관리자 전용 명령어입니다! It's only for Admin")
        
        elif isinstance(error, commands.NotOwner):
            await ctx.send("개발자 전용 명령어입니다! It's only for Bot owner")
        
        elif isinstance(error, commands.errors.UserNotFound):
            await ctx.send("유저는 멘션이나 ID복사로 전달해주세요!")
        
        elif isinstance(error, discord.errors.HTTPException):
            if error.code != 429:   # Too Many Requests
                embed = discord.Embed(title="Bug report", timestamp=now())
                embed.add_field(name="error string", value=str(error), inline=False)
                embed.add_field(name="error invoked with", value=ctx.invoked_with, inline=False)
                embed.add_field(name="full context", value=ctx.message.content, inline=False)
                await self.ErrLogCh.send(embed=embed)
                await ctx.send("잠시 오류가 나서, 개발자에게 버그 리포트를 작성해줬어요! 곧 고칠 예정이니 잠시만 기다려주세요 :)")
        
        else:
            embed = discord.Embed(title="Bug report", timestamp=now())
            embed.add_field(name="error string", value=str(error), inline=False)
            embed.add_field(name="error invoked with", value=ctx.invoked_with, inline=False)
            embed.add_field(name="full context", value=ctx.message.content, inline=False)
            await self.ErrLogCh.send(embed=embed)
            await ctx.send("잠시 오류가 나서, 개발자에게 버그 리포트를 작성해줬어요! 곧 고칠 예정이니 잠시만 기다려주세요 :)")

def setup(bot):
    bot.add_cog(CogEvent(bot))
