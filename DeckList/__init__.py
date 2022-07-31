from .Commands import CogDeckList, MyBot

async def setup(bot: MyBot):
    await bot.add_cog(CogDeckList(bot), bot.target_guild)
