from .Commands import CogDetect, MyBot

async def setup(bot: MyBot):
    await bot.add_cog(CogDetect(bot), guild=bot.target_guild)
