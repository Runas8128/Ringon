from Common import *

class CogDebug(MyCog, name='디버그'):
    """
    디버그용 커맨드 그룹입니다.
    개발자 전용 커맨드 그룹이며, 굳이 써봐야 볼 내용도 많이 없습니다.
    """

    def __init__(self, bot):
        self.bot = bot
        
        self.AdminOnly = []
        self.OwnerOnly = [self.cmd_ShowDB, self.cmd_ShowDBKey]

        self.EngCmd = [self.cmd_ShowDB, self.cmd_ShowDBKey]
        self.KorCmd = [self.cmd_ShowDB, self.cmd_ShowDBKey]
    
    @commands.command(
        name='show',
        brief='DB를 보여줍니다. 디버그용 명령어입니다.',
        description='DB의 내용을 보여줍니다. 디버그용 명령어로, 거의 쓸 일이 없는 명령어입니다.',
        usage='!show (키 나열)'
    )
    @commands.is_owner()
    async def cmd_ShowDB(self, ctx: commands.Context, mainKey: str = 'None', *keys: str):
        if mainKey in db.keys():
            d = db[mainKey]
            for key in keys:
                if isinstance(d, dict) and (key in d.keys()):
                    d = d[key]
                else:
                    await ctx.send(f'{key} not in {d}')
                    return
            await ctx.send(d)
        else:
            await ctx.send(f'{mainKey} not in {db.keys()}')

    @commands.command(
        name='showKey',
        brief='DB의 키를 보여줍니다. 디버그용 명령어입니다.',
        description='DB의 키를 보여줍니다. 디버그용 명령어로, 거의 쓸 일이 없는 명령어입니다.',
        usage='!showKey (키 나열)'
    )
    @commands.is_owner()
    async def cmd_ShowDBKey(self, ctx: commands.Context, mainKey: str = None, *keys: str):
        if mainKey in db.keys():
            d = db[mainKey]
            for key in keys:
                if isinstance(d, dict) and (key in d.keys()):
                    d = d[key]
                else:
                    await ctx.send(f'{key} not in {d}')
                    return
            if isinstance(d, dict):
                await ctx.send(d.keys())
            else:
                await ctx.send(d)
        elif mainKey == None:
            await ctx.send(db.keys())
        else:
            await ctx.send(f'{mainKey} not in {db.keys()}')

def setup(bot):
    bot.add_cog(CogDebug(bot))