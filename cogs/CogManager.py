import discord
from discord.ext import commands

from util.myBot import MyBot

class CogManager(commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.all_cog = ['Events', 'DeckList', 'Detect', 'birthday', 'Other']
    
    async def load_all(self):
        for cogName in self.all_cog:
            await self._load(cogName)
    
    async def checkMe(self, ctx: commands.Context, me: discord.User):
        """|coro|
        
        Check if mentioned this bot when calling below commands

        Parameters
        ----------
        * ctx: :class:`discord.ext.commands.Context`
            - Context of calling command
        * me: :class:`discord.User`
            - Bot user, which must be equal to this running bot.

        Return Value
        ------------
        True if the command may run, else False
        
        ."""

        if not me:
            await ctx.send("mention me when running command!")
            return False
        
        if me != self.bot.user:
            return False
        
        return True
    
    async def _load(self, name: str):
        """|coro|

        this coroutine loads extension, ignore `NotLoaded` exception.
        """
        try:
            await self.bot.load_extension('cogs.' + name)
        except commands.ExtensionNotLoaded:
            pass
    
    async def _unload(self, name: str):
        """|coro|

        this coroutine unloads extension, ignore `AlreadyLoaded` exception.
        """
        try:
            await self.bot.unload_extension('cogs.' + name)
        except commands.ExtensionAlreadyLoaded:
            pass

    @commands.command()
    @commands.is_owner()
    async def debug(self, ctx: commands.Context, me: discord.User=None, onoff: bool=True):
        if not await self.checkMe(ctx, me):
            return
        
        if onoff:
            await self._load('util.Debug')
        else:
            await self._unload('util.Debug')
        await ctx.message.add_reaction('👍')
    
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, me: discord.User=None, CogName: str = ''):
        if not await self.checkMe(ctx, me):
            return
        
        if CogName == 'CogManager':
            await ctx.send("[Error] Cog Manager can only be loaded in code")
            return
        
        try:
            await self._load(CogName)
            await ctx.send(f"Successfully loaded Cog {CogName}")
        except commands.ExtensionNotFound:
            await ctx.send(f"Cannot find that Cog. You can load: {self.all_cog}")
    
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, me: discord.User=None, CogName: str = ''):
        if not await self.checkMe(ctx, me):
            return
        
        if CogName == 'CogManager':
            await ctx.send("[Error] Cog Manager cannot be unloaded")
            return
        
        try:
            await self._unload(CogName)
            await ctx.send(f"Successfully unloaded Cog {CogName}")
        except commands.ExtensionNotFound:
            await ctx.send(f"Cannot find that Cog. You can unload: {self.all_cog}")
    
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, me: discord.User=None, CogName: str = ''):
        if not await self.checkMe(ctx, me):
            return
        
        if CogName == 'CogManager':
            await ctx.send("[Error] Cog Manager cannot be reloaded")
            return
        
        if CogName:
            try:
                await self._unload(CogName)
                await self._load(CogName)
                await ctx.send(f"Successfully reloaded Cog {CogName}")
            except commands.ExtensionNotFound:
                await ctx.send(f"Cannot find that Cog. You can load: {self.all_cog}")
        
        else:
            success = self.all_cog[:]
            for cogName in success:
                try:
                    await self._unload(CogName)
                    await self._load(CogName)
                except:
                    success.remove(cogName)
                    await ctx.send(f"Reloading Cog {cogName} Failed, skipping...")
            await ctx.send(f"Successfully reload All Cogs: {success}")

async def setup(bot: MyBot):
    manager = CogManager(bot)
    await manager.load_all()

    await bot.add_cog(manager, guild=bot.target_guild)
