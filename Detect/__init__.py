from .Commands import CogDetect

def setup(bot):
    bot.add_cog(CogDetect(bot))
