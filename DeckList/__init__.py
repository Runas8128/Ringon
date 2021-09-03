from .Commands import CogDeckList

def setup(bot):
    bot.add_cog(CogDeckList(bot))