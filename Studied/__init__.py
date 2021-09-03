from discord.ext.commands.cog import Cog
from .Commands import CogStudied

def setup(bot):
    bot.add_cog(CogStudied(bot))