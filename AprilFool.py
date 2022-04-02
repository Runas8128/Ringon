from typing import List, Union, Tuple

from Common import *

class OverWrite:
    def __init__(
        self,
        noChangeCh: List[int],
        view_channel: bool = None, connect: bool = None, send_messages: bool = None
    ):
        self.view_channel = view_channel
        self.connect = connect
        self.send_messages = send_messages
        self.noChangeCh = noChangeCh
    
    def toDict(self, revert: bool):
        dc = {}
        if self.view_channel != None:
            dc['view_channel'] = self.view_channel if not revert else not self.view_channel
        if self.connect != None:
            dc['connect'] = self.connect if not revert else not self.connect
        if self.send_messages != None:
            dc['send_messages'] = self.send_messages if not revert else not self.send_messages
        
        return dc

class AprilFoolCog(MyCog, name="만우절"):
    """
    만우절 커맨드를 담고 있는 파일입니다.
    장난식의 커맨드이니, 주의해주세요!
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.updateList = {
            758478112979288094: {
                None: OverWrite(
                    noChangeCh=[
                        864518975253119007
                    ],
                    send_messages=True
                ),
                843796108345081856: OverWrite(
                    noChangeCh=[
                        844229601504133150
                    ],
                    view_channel=True, connect=True
                ),
                764819837305749514: OverWrite(
                    noChangeCh=[],
                    view_channel=False
                ),
                758478112979288099: OverWrite(
                    noChangeCh=[],
                    view_channel=False, connect=False
                ),
                891697283702345798: OverWrite(
                    noChangeCh=[],
                    view_channel=False
                ),
                758478112979288095: OverWrite(noChangeCh=[]), # No Change
                789732418378006538: OverWrite(
                    noChangeCh=[
                        790850193649696768,
                        765958359382884402,
                        957912662551961661,
                        809342346466557952
                    ],
                    view_channel=True, connect=True, send_messages=True
                ),
                870332556132896769: OverWrite(noChangeCh=[]), # No Change
                864155712988905472: OverWrite(noChangeCh=[]), # No Change
                902845024176312420: OverWrite(noChangeCh=[]), # No Change
            },
            783257655388012584: {
                None: OverWrite(
                    noChangeCh=[
                        959078169980321792
                    ],
                    connect=True, send_messages=True
                ),
                958338514238464010: OverWrite(
                    noChangeCh=[
                        783257655388012587
                    ],
                    view_channel=False, connect=False, send_messages=False
                ),
                958689840680013856: OverWrite(
                    noChangeCh=[
                        955800123089256468
                    ],
                    view_channel=True, send_messages=True, connect=True
                ),
                843797752739266560: OverWrite(
                    noChangeCh=[
                        843797755704770601,
                        843797758602510338,
                        843797761652162580
                    ],
                    view_channel=True, connect=True
                )
            }
        }

    async def Execute(self, guild: discord.Guild, revert: bool):
        overWriteList = self.updateList[guild.id]
        default_role = guild.default_role

        for channel in guild.channels:
            category = channel.category
            if category != None:
                overWrite = overWriteList[channel.category_id]
            else:
                overWrite = overWriteList[None]
            
            if channel.id in overWrite.noChangeCh and not revert:
                continue

            await channel.set_permissions(
                target=default_role,
                overwrite=discord.PermissionOverwrite(**overWrite.toDict(revert=revert))
            )
            print(f'set #{channel.name}: {overWrite.toDict(revert=revert)}')

    @commands.command(
        name='만우절',
        brief='[데이터 말소됨]',
        description='[데이터 말소됨]',
        usage='[데이터 말소됨]'
    )
    @commands.has_permissions(administrator=True)
    async def RG_AprilFool(self, ctx: commands.Context, run: str=''):
        guild: discord.Guild = ctx.guild

        if self.updateList.get(guild.id, None) == None:
            print('This guild is not allowed')
            return

        if run == '실행':
            await self.Execute(guild, False)
            
        elif run == '실행취소':
            await self.Execute(guild, True)

def setup(bot):
    bot.add_cog(AprilFoolCog(bot))
