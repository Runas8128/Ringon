import discord
from discord import app_commands
from discord.ext import commands

from util.myBot import MyBot

class CogManager(commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.all_cog = self.bot.testCogs or ['Events', 'DeckList', 'Detect', 'Birthday', 'Check', 'Other']
    
    async def load_all(self):
        for cogName in self.all_cog:
            await self._load(cogName)
    
    async def _load(self, name: str):
        """|coro|

        this coroutine loads extension, ignore `NotLoaded` exception.
        """
        try:
            await self.bot.load_extension('cogs.' + name)
            print(f"Loaded {name}")
        except commands.ExtensionAlreadyLoaded:
            print(f"Skipping loading cog {name}: Already loaded")
    
    async def _unload(self, name: str):
        """|coro|

        this coroutine unloads extension, ignore `AlreadyLoaded` exception.
        """
        try:
            await self.bot.unload_extension('cogs.' + name)
            print(f"Unloaded {name}")
        except commands.ExtensionNotLoaded:
            print(f"Skipping unloading cog {name}: Not loaded")

    @app_commands.command(
        name="ㅎ_manage",
        description="[개발자 전용] 특정 커맨드 그룹을 로드하거나 언로드합니다."
    )
    @app_commands.describe(
        name="대상 커맨드 그룹을 지정합니다.",
        option="실행할 행동을 지정합니다."
    )
    @app_commands.choices(
        name=[
            app_commands.Choice(name='Events',      value='Events'),
            app_commands.Choice(name='DeckList',    value='DeckList'),
            app_commands.Choice(name='Detect',      value='Detect'),
            app_commands.Choice(name='Birthday',    value='Birthday'),
            app_commands.Choice(name='Check',       value='Check'),
            app_commands.Choice(name='Other',       value='Other'),
            app_commands.Choice(name='Debug',       value='Debug'),
        ],
        option=[
            app_commands.Choice(name="Load",    value="load"),
            app_commands.Choice(name="Unload",  value="unload"),
            app_commands.Choice(name="Reload",  value="reload")
        ]
    )
    async def manage(self, interaction: discord.Interaction, name: str, option: str):
        if interaction.user.id == self.bot.owner_id or interaction.user.id in self.bot.owner_ids:
            if option == "load":
                await self._load(name)
            elif option == "unload":
                await self._unload(name)
            elif option == "reload":
                await self._unload(name)
                await self._load(name)
            await interaction.response.send_message("Success", ephemeral=True)
        else:
            await interaction.response.send_message("해당 명령어는 개발자 전용 명령어입니다.", ephemeral=True)
            print(interaction.user.id, self.bot.owner_id, self.bot.owner_ids)
    
    @app_commands.command(
        name="ㅎ_reload",
        description="[개발자 전용] 현재 테스트중인 / 구동중인 모든 커맨드 그룹을 다시 로드합니다."
    )
    async def reload(self, interaction: discord.Interaction):
        if interaction.user.id == self.bot.owner_id or interaction.user.id in self.bot.owner_ids:
            await interaction.response.defer()

            success = self.all_cog[:]
            await interaction.followup.send(f"Reloading cogs... target = {self.all_cog}", ephemeral=True)
            for cogName in success:
                try:
                    await self._unload(CogName)
                    await self._load(CogName)
                except:
                    success.remove(cogName)
                    await interaction.followup.send(f"Reloading Cog {cogName} Failed, skipping...", ephemeral=True)
            await interaction.followup.send(f"Successfully reload All Cogs: {success}", ephemeral=True)
        else:
            await interaction.response.send_message("해당 명령어는 개발자 전용 명령어입니다.", ephemeral=True)
            print(interaction.user.id, self.bot.owner_id, self.bot.owner_ids)

async def setup(bot: MyBot):
    manager = CogManager(bot)
    await manager.load_all()

    await bot.add_cog(manager, guild=bot.target_guild)
