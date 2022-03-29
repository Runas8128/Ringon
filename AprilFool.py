from typing import List, Union, Tuple

from Common import *

class AprilFoolCog(MyCog, name="만우절"):
    """
    만우절 커맨드를 담고 있는 파일입니다.
    장난식의 커맨드이니, 주의해주세요!
    """

    async def Execute(self, guild: discord.Guild):
        pass

    async def Undo(self, guild: discord.Guild):
        pass

    @commands.command(
        name='만우절',
        brief='[데이터 말소됨]',
        description='[데이터 말소됨]',
        usage='[데이터 말소됨]'
    )
    @commands.has_permissions(administrator=True)
    async def RG_AprilFool(self, ctx: commands.Context, run: str=''):
        guild: discord.Guild = ctx.guild

        if guild.id not in [783257655388012584, 823359663973072957]:
            print('guild is not test server')
            return

        if run == '실행':
            for ch in guild.channels:
                overwrite = ch.overwrites_for(guild.default_role)
                
                # 채널이 주요 관리자실인 경우
                if ch.id in [955800123089256468]:
                    newOverwrite = discord.PermissionOverwrite()
                    newOverwrite.view_channel = True
                    newOverwrite.send_messages = True
                    await ch.set_permissions(guild.default_role, overwrite=newOverwrite)
                    print(f'channel {ch.name}: view_channel: False -> True')
                
                # 채널이 모두가 쓸 수 있는 경우
                elif overwrite.send_messages in [True, None]:
                    newOverwrite = discord.PermissionOverwrite()
                    newOverwrite.send_messages = False
                    await ch.set_permissions(guild.default_role, overwrite=newOverwrite)
                    print(f'channel {ch.name}: send_message: True -> False')
            
        elif run == '실행취소':
            for ch in guild.channels:
                overwrite = ch.overwrites_for(guild.default_role)
                
                # 채널이 주요 관리자실인 경우
                if ch.id in [955800123089256468]:
                    newOverwrite = discord.PermissionOverwrite()
                    newOverwrite.view_channel = False
                    newOverwrite.send_messages = False
                    await ch.set_permissions(guild.default_role, overwrite=newOverwrite)
                    print(f'channel {ch.name}: view_channel: True -> False')
                
                # 채널이 모두가 쓸 수 있는 경우
                elif overwrite.send_messages == False:
                    newOverwrite = discord.PermissionOverwrite()
                    newOverwrite.send_messages = True
                    await ch.set_permissions(guild.default_role, overwrite=newOverwrite)
                    print(f'channel {ch.name}: send_message: False -> True')

def setup(bot):
    bot.add_cog(AprilFoolCog(bot))
