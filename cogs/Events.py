import io
from time import time

import discord
from discord.ext import commands

from database import util
from util import now
from ringon import Ringon

class CogEvent(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot

        self.error_log_channel: discord.TextChannel = None
        self.admin_channel: discord.TextChannel = None

        util.load()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game("덱, 프로필, 전적을 관리")
        )

        self.error_log_channel = self.bot.get_channel(863719856061939723)
        if self.bot.is_testing:
            self.admin_channel = self.bot.get_channel(823359663973072960)
        else:
            self.admin_channel = self.bot.get_channel(783539105374928986)

        await self.bot.get_channel(1005348204965015563).send(
            f"Ringon is alive since <t:{int(time())}>"
        )

    @commands.Cog.listener()
    async def on_message(self,
        message: discord.Message
    ):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.channel.DMChannel):
            files = None
            if len(message.attachments) > 0:
                files = [
                    discord.File(io.BytesIO(await file.read()), file.filename)
                    for file in message.attachments
                ]

            await self.admin_channel.send(
                f"{message.author.mention}님의 DM입니다!\n" + \
                message.content,
                files=files
            )
            return

        for block in util.block_words:
            if block in message.content:
                await message.channel.send(
                    f'금칙어 {block[0]}읍읍이 포함되었습니다',
                    delete_after=5
                )
                await message.delete()
                return

    @commands.Cog.listener()
    async def on_thread_create(self,
        thread: discord.Thread
    ):
        if self.bot.is_testing:
            await thread.send("Hello! I found some new thread")
        else:
            await thread.add_user(discord.Object(272266200812093441))

    @commands.Cog.listener()
    async def on_command_error(self,
        ctx: commands.Context,
        error
    ):
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("관리자 전용 명령어입니다! It's only for Admin")

        elif isinstance(error, commands.NotOwner):
            await ctx.send("개발자 전용 명령어입니다! It's only for Bot owner")

        elif isinstance(error, discord.errors.HTTPException) and error.code == 429:
            return

        await self.error_log_channel.send(
            embed=discord.Embed(
                title="Bug report", timestamp=now()
            ).add_field(
                name="error string", value=str(error), inline=False
            ).add_field(
                name="error invoked with", value=ctx.invoked_with, inline=False
            ).add_field(
                name="full context", value=ctx.message.content, inline=False
            )
        )
        await ctx.send(
            "잠시 오류가 나서, 개발자에게 버그 리포트를 작성해줬어요! "
            "곧 고칠 예정이니 잠시만 기다려주세요 :)"
        )

async def setup(bot: Ringon):
    await bot.add_cog(CogEvent(bot), guild=bot.target_guild)
