import asyncio
import requests

import discord
from discord import app_commands

from util.deckList import deckList
from util.view import DeckListView
from util.myBot import MyBot

class CogDeckList(commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        deckList.loadHistCh(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """ Detect all message

        If message is in `Lab` category and has attached image
            add a reaction (which is not in WMTD Server, but Bot server)
        """
        if message.channel.category.name != "LAB":
            # This auto-add logic only deal with `Lab` category
            return
        
        if len(message.attachments) == 0:
            # This auto-add logic triggered when the message has at least one attachment
            return
        
        if message.channel.name in ["덱리커스텀_상성확인실", "unlimited", "2pick"]:
            # This auto-add Logic is not triggered in above channels
            return
        
        await message.add_reaction("<:Tldlr:805678671527936010>")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """ Detect all reaction even if origin message is not in cache
        
        If reaction is pre-defined emoji
            proceed deck add logic
        """
        if not (isinstance(payload.emoji, discord.Emoji) and payload.emoji.id != 805678671527936010):
            # This auto-add Logic triggered with this emoji
            return
        
        channel: discord.TextChannel = self.bot.get_channel(payload.channel_id)
        orgMsg = await channel.fetch_message(payload.message_id)
        
        if msgOrg.author != payload.member:
            # This auto-add Logic triggered when author add reaction
            return
        
        try:
            while True:
                name = await self.getDeckName(orgMsg)

                if deckList.hasDeck(name):
                    if await self.getIfUpdate(orgMsg):
                        await self._updateDeck(orgMsg, name)
                        return
                    else:
                        continue
                else:
                    await self._addDeck(orgMsg, name)
                    return
        except asyncio.TimeoutError:
            await channel.send("시간 초과, 덱 등록을 취소합니다.")
            return
    
    @app_commands.command(
        name="덱검색",
        description="DB에 저장된 덱을 검색합니다."
    )
    @app_commands.describe(
        query="검색할 키워드를 입력합니다. 공백을 기준으로 분리해 덱 이름이나 덱 설명에서만 검색합니다.",
        clazz="검색할 클래스를 지정합니다.",
        author="검색할 덱의 작성자/기여자를 선택합니다."
    )
    @app_commands.choices(
        clazz=[
            app_commands.Choice(name="엘프",        value="엘프"),
            app_commands.Choice(name="로얄",        value="로얄"),
            app_commands.Choice(name="위치",        value="위치"),
            app_commands.Choice(name="드래곤",      value="드래곤"),
            app_commands.Choice(name="네크로맨서",  value="네크로맨서"),
            app_commands.Choice(name="뱀파이어",    value="뱀파이어"),
            app_commands.Choice(name="비숍",        value="비숍"),
            app_commands.Choice(name="네메시스",    value="네메시스")
        ]
    )
    async def cmdSearchDeck(
        self, interaction: discord.Interaction,
        query: str = None,
        clazz: str = None,
        author: discord.Member = None
    ):
        await interaction.response.send_message(
            view=DeckListView(interaction, deckList.searchDeck(query or [], clazz, author))
        )
    
    @app_commands.command(
        name="포탈링크",
        description="덱 코드를 입력하면, 그 포탈로 가는 버튼을 만들어줍니다."
    )
    @app_commands.describe(
        DeckCode="포탈 링크를 만들 덱 코드입니다."
    )
    async def RG_LinkPortal(self, interaction: discord.Interaction, DeckCode: str):
        response = requests.get(
            'https://shadowverse-portal.com/api/v1/deck/import',
            params={'format': 'json', 'deck_code': DeckCode}
        )
        d = response.json()['data']
        if len(d['errors']) > 0:
            await interaction.response.send_message("덱 코드가 무효하거나, 잘못 입력되었습니다. 다시 입력해 주시기 바랍니다.")
        else:
            clan, hash = d['clan'], d['hash']
            deckURL, imageURL = f'https://shadowverse-portal.com/deck/{hash}', f'https://shadowverse-portal.com/image/{hash}'

            portalEmbed = discord.Embed(title="포탈 연결 성공!").set_image(url=imageURL)
            linkButton = discord.ui.Button(label="포탈 링크", style=discord.ButtonStyle.blurple, url=deckURL)
            linkView = discord.ui.View(); linkView.add_item(linkButton)
            
            await interaction.response.send_message(embed=portalEmbed, view=linkView)

    async def _addDeck(self, orgMsg: discord.Message, name: str):
        """|coro|
        front-end method for adding deck in database

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        * name: :class:`str`
            - name of deck which will be added
            - WARNING: deck with same name should not be in database

        ."""
        try:
            desc = await self.getDeckDesc(orgMsg)
        except asyncio.TimeoutError:
            await orgMsg.channel.send("시간 초과, 덱 등록을 취소합니다.")
            return

        clazz = channel.name
        imageURL = msgOrg.attachments[0].url
        author = msgOrg.author.id

        deckList.addDeck(name, clazz, desc, imageURL, author)
        await orgMsg.reply("덱 등록을 성공적으로 마쳤습니다!")
    
    async def _updateDeck(self, orgMsg: discord.Message, name: str):
        """|coro|
        front-end method for updating deck in database

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        * name: :class:`str`
            - name of deck which will be updated
            - WARNING: deck with same name should be in database

        ."""
        try:
            desc = await self.getDeckDesc(orgMsg)
        except:
            await orgMsg.channel.send("시간 초과, 덱 업데이트를 취소합니다.")
            return
        
        imageURL = '' if len(msgOrg.attachments) == 0 else orgMsg.attachments[0].url
        
        try:
            deckList.updateDeck(name, orgMsg.author.id, imageURL=imageURL, desc=desc)
            await orgMsg.reply("덱 업데이트를 성공적으로 마쳤습니다!")
        except ValueError as v:
            await orgMsg.reply(str(v))

    async def getDeckName(self, orgMsg: discord.Message):
        """ get deck name with origin message

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        
        Return value
        ------------
        return got deck name

        Raises
        ------
        `asyncio.TimeoutError` when timeout(1min)

        ."""
        def check(message: discord.Message):
            return orgMsg.author == message.author and orgMsg.channel == message.channel
        
        await orgMsg.reply(embed=discord.Embed(
            title=":ledger: 덱의 이름을 입력해주세요!",
            description="시간 제한: 1분"
        ), mention_author=False)
        
        msgName: discord.Message = await self.bot.wait_for('message', check=check, timeout=60.0)
        return msgName.content
    
    async def getIfUpdate(self, orgMsg: discord.Message):
        """ get boolean data whether update deck or re-input name

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        
        Return value
        ------------
        return if author selected update

        Raises
        ------
        `asyncio.TimeoutError` when timeout(1min)

        ."""
        def check(message: discord.Message):
            return orgMsg.author == message.author and orgMsg.channel == message.channel and message.content in ["재입력", "업데이트"]
        
        await orgMsg.reply(embed=discord.Embed(
            title=":pause_button: 이미 있는 덱 이름입니다!",
            description="이름을 바꾸려면 `재입력`을, 덱을 업데이트하려면 `업데이트`를 입력해주세요.\n시간 제한: 1분"
        ), mention_author=False)
        
        msgCheck: discord.Message = await self.bot.wait_for('message', check=checkCorrectInput, timeout=60.0)
        return msgCheck.content == "업데이트"
    
    async def getDeckDesc(self, orgMsg: discord.Message):
        """ get description of deck

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        
        Return value
        ------------
        return got description

        Raises
        ------
        `asyncio.TimeoutError` when timeout(15min)

        ."""
        def check(message: discord.Message):
            return orgMsg.author == message.author and orgMsg.channel == message.channel
        
        await orgMsg.reply(embed=discord.Embed(
            title=":ledger: 덱의 설명을 입력해주세요!",
            description="시간 제한: 15분\n덱 설명을 생략하려면 `생략`을 입력해주세요."
        ), mention_author=False)

        msgDesc: discord.Message = await self.bot.wait_for('message', check=check, timeout=60.0 * 15)

        desc = msgDesc.content.strip()
        if desc == "생략": desc = ""
        return desc

async def setup(bot: MyBot):
    await bot.add_cog(CogDeckList(bot), guild=bot.target_guild)

""" 
    async def Similar(self, ctx: commands.Context, Name: str, lang: Lang):
        await ctx.send(self.T.translate('Similar.FindFail', lang).format(Name))
        
        similar = deckList.similar(Name)
        if similar:
            embed = discord.Embed(
                title='이런 덱을 찾으셨나요?' if lang == 'KR' else 'Did you find...',
                color=0x2b5468
            )
            for deck in similar:
                embed.add_field(
                    name=self.makeTitle(deck),
                    value=f"{'클래스' if lang == 'KR' else 'Class'}: {deck['class']}"
                )
            await ctx.send(embed=embed)
    
    async def Delete(self, ctx: commands.Context, Name: str, SendHistory:bool, lang: Lang):
        delDeck = [deck for deck in deckList.List if deck['name'] == Name]
        
        if delDeck: # Deck found
            if not deckList.hisCh: # history channel is not made yet
                deckList.hisCh = self.bot.get_channel(804614670178320394)
            
            embed = self.makeEmbed(deckList.delete(Name), lang)
            
            if SendHistory:
                await deckList.hisCh.send(embed=embed)
            await ctx.send(self.T.translate('Delete.Success', lang).format(Name))
        
        else: # cannot find Deck
            await self.Similar(ctx, Name, lang)
    
    @commands.command(name='덱삭제')
    async def RG_Delete_KR(self, ctx: commands.Context, Name: str='', SendHistory:bool=True):
        await self.Delete(ctx, Name, SendHistory, 'KR')
    
    @commands.command(name='delete', aliases=['remove', 'del', 'rem'])
    async def RG_Delete_EN(self, ctx: commands.Context, Name: str='', SendHistory:bool=True):
        await self.Delete(ctx, Name, SendHistory, 'EN')
    
    @commands.command(name='덱분석')
    async def RG_Analyze_KR(self, ctx: commands.Context):
        await ctx.send(embed=deckList.analyze('KR'))
    
    @commands.command(name='analyze')
    async def RG_Analyze_EN(self, ctx: commands.Context):
        await ctx.send(embed=deckList.analyze('EN'))
    
    @commands.command(name='팩이름')
    @commands.has_permissions(administrator=True)
    async def RG_Pack(self, ctx: commands.Context, newPack: str=''):
        if newPack == '':
            await ctx.send('사용법: !팩이름 (새 팩 이름)\n**주의 - 모든 로테이션 덱이 삭제됩니다**')
            return
        
        db['pack'] = newPack
        await ctx.send(f'팩 이름을 {newPack}으로 바꿨어요!')
        
        if not deckList.hisCh:
            deckList.hisCh = self.bot.get_channel(804614670178320394)
        
        for deck in deckList.deleteRT():
            await deckList.hisCh.send(embed=self.makeEmbed(deck, 'KR'))
    
    @commands.command(name="세부분석")
    async def RG_DeepAnalyze(self, ctx: commands.Context):
        deckList: List[Deck] = deckList.List
        rt = [deck for deck in deckList if deck['rtul'] == 'RT']
        ul = [deck for deck in deckList if deck['rtul'] == 'UL']
        
        s = '**제작자 ID/멘션** - (추가 / 기여)\n'
        
        s += '**로테이션**\n'
        for author in set([deck['author'] for deck in rt]):
            write = [1 if deck['author'] == author else 0 for deck in rt]
            cont = [1 if ('cont' in deck and author in deck['cont']) else 0 for deck in rt]
            s += f'{author} - {sum(write)} / {sum(cont)}\n'
        
        s += '**언리미티드**\n'
        for author in set([deck['author'] for deck in ul]):
            write = [1 if deck['author'] == author else 0 for deck in ul]
            cont = [1 if ('cont' in deck and author in deck['cont']) else 0 for deck in ul]
            s += f'{author} - {sum(write)} / {sum(cont)}\n'
        
        await ctx.send(s)
"""
