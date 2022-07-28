import discord
from discord.ext import commands

class CogManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.all_cog = ['Events', 'DeckList', 'Detect', 'Other']
        
        for cogName in self.all_cog:
            self.bot.load_extension(cogName)
    
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
    
    @commands.command()
    @commands.is_owner()
    async def debug(self, ctx: commands.Context, me: discord.User=None, onoff: bool=True):
        if await self.checkMe(ctx, me):
            if onoff:
                try:
                    self.bot.load_extension('Debug')
                except commands.ExtensionAlreadyLoaded:
                    pass
            else:
                try:
                    self.bot.unload_extension('Debug')
                except commands.ExtensionNotLoaded:
                    pass
            await ctx.message.add_reaction('👍')
    
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, me: discord.User=None, CogName: str = ''):
        if await self.checkMe(ctx, me):
            if CogName == 'CogManager':
                await ctx.send("[Error] Cog Manager can only be loaded in code")
                return
            
            try:
                self.bot.load_extension(CogName)
                await ctx.send(f"Successfully loaded Cog {CogName}")
            except commands.ExtensionAlreadyLoaded:
                pass
            except commands.ExtensionNotFound:
                await ctx.send(f"Cannot find that Cog. You can load: {self.all_cog}")
    
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, me: discord.User=None, CogName: str = ''):
        if await self.checkMe(ctx, me):
            if CogName == 'CogManager':
                await ctx.send("[Error] Cog Manager cannot be unloaded")
                return
            
            try:
                self.bot.unload_extension(CogName)
                await ctx.send(f"Successfully unloaded Cog {CogName}")
            except commands.ExtensionNotLoaded:
                pass
    
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, me: discord.User=None, CogName: str = ''):
        if await self.checkMe(ctx, me):
            if CogName == 'CogManager':
                await ctx.send("[Error] Cog Manager cannot be reloaded")
                return
            
            if CogName:
                try:
                    self.bot.unload_extension(CogName)
                except commands.ExtensionNotLoaded:
                    pass
                try:
                    self.bot.load_extension(CogName)
                except commands.ExtensionAlreadyLoaded:
                    pass
                
                await ctx.send(f"Successfully reloaded Cog {CogName}")
            
            else:
                success = self.all_cog[:]
                for cogName in success:
                    try:
                        self.bot.unload_extension(cogName)
                        self.bot.load_extension(cogName)
                    except:
                        success.remove(cogName)
                        await ctx.send(f"Reloading Cog {cogName} Failed, skipping...")
                await ctx.send(f"Successfully reload All Cogs: {success}")

def setup(bot):
    bot.add_cog(CogManager(bot))
