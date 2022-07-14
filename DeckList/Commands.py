import asyncio
import requests

from .Helper import *

class CogDeckList(MyCog, name="덱"):
    """덱리를 저장하고 구경하는 카테고리입니다.
    Command category for storing/viewing Decklist
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.T = Translator('DeckList')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """ Detect all message

        If message is in `Lab` category and has attached image
            add a reaction (which is not in WMTD Server, but Bot server)
        """
        if message.channel.category_id != 891697283702345798:
            # This auto-add logic only deal with `Lab` category
            return
        
        if len(message.attachments) == 0:
            # This auto-add logic triggered when the message has at least one attachment
            return
        
        if message.channel.id in [984745573406085160, 984746283430469652, 984746309573550080]:
            # This auto-add Logic is not triggered in above channels
            return
        
        await message.add_reaction("<:Tldlr:805678671527936010>")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """ Detect all reaction even if origin message is not in cache
        
        If reaction is pre-defined emoji
            proceed deck add logic
        """
        if not isinstance(payload.emoji, discord.Emoji) or payload.emoji.id != 805678671527936010:
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

                if DeckList.hasDeck(name):
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

        DeckList.addDeck(name, clazz, desc, imageURL, author)
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
        
        if len(msgOrg.attachments) > 0:
            imageURL = orgMsg.attachments[0].url
        else:
            imageURL = ''
        
        try:
            DeckList.updateDeck(name, orgMsg.author.id, imageURL=imageURL, desc=desc)
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
            return orgMsg.author == message.author
        
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
            return orgMsg.author == message.author and message.content in ["재입력", "업데이트"]
        
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
            return orgMsg.author == message.author
        
        await orgMsg.reply(embed=discord.Embed(
            title=":ledger: 덱의 설명을 입력해주세요!",
            description="시간 제한: 15분\n덱 설명을 생략하려면 `생략`을 입력해주세요."
        ), mention_author=False)

        msgDesc: discord.Message = await self.bot.wait_for('message', check=check, timeout=60.0 * 15)

        desc = msgDesc.content.strip()
        if desc == "생략": desc = ""
        return desc

"""
    def makeTitle(self, deck: Deck, KE: Lang = 'KR') -> str:
        name = deck['name']
        ver  = '' if not deck.get('ver') else f" ver. {deck['ver']}"
        rtul = eval(deck['rtul'])
        pack = '' if deck['rtul'] == 'UL' else f", {db['pack']} {'팩' if KE == 'KR' else 'Pack'}"
        return f"{name}{ver}({rtul}{pack})"
    
    def makeEmbed(self, deck: Deck, KE: Lang = 'KR') -> discord.Embed:
        uploader: str
        
        if deck['author'].startswith('<@!') or deck['author'].startswith('<@'):
            uploader = deck['author']
        else:
            uploader = self.bot.get_user(int(deck['author'])).mention
        
        embed = discord.Embed(
            title=self.makeTitle(deck, KE),
            color=0x2b5468
        )
        embed.add_field(name="업로더" if KE == 'KR' else "Uploader", value=uploader, inline=False)
        embed.add_field(name="클래스" if KE == 'KR' else "Class", value=deck['class'], inline=False)
        
        if deck.get('date'):
            embed.add_field(name='올린 날짜' if KE == 'KR' else 'Date', value=deck['date'])
        if deck.get('cont'):
            embed.add_field(name='기여자' if KE == 'KR' else 'Contributor', value=', '.join(deck['cont']))
        
        embed.set_image(url=deck['imgURL'])
        
        return embed
    
    # ----- Command Helper -----
    
    async def Find(self, ctx: commands.Context, scThings: List[str], lang: Lang):
        if not scThings:
            await ctx.send(self.T.translate('Find.NoWord', lang))
            return
        
        foundDeck = DeckList.find(lambda deck: deck['name'] == scThings[0].upper())
        
        if not foundDeck:
            scFuncS = "lambda deck: True"
            
            for scThing in scThings:
                Class = strToClass(scThing)
                
                if   scThing.lower() in ['로테이션',   '로테', 'rotation', 'rt']:
                    scFuncS += " and deck['rtul'] == 'RT'"
                elif scThing.lower() in ['언리미티드', '언리', 'unlimited', 'ul']:
                    scFuncS += " and deck['rtul'] == 'UL'"
                
                elif scThing.startswith('<@'):
                    scFuncS += f''' and deck['author'] == "{scThing[2:-1].replace('!', '')}"'''
                
                elif Class in OrgCls:
                    scFuncS += f" and '{Class}' == deck['class']"
                
                else:
                    scFuncS += f" and '{scThing.upper()}' in deck['name']"
            
            foundDeck = DeckList.find(eval(scFuncS))
        
        if len(foundDeck) == 0:
            await ctx.send(self.T.translate('Find.NoMatchDeck', lang))
        else:
            if len(foundDeck) > 25:
                await ctx.send(self.T.translate('Find.TooManyDeck', lang))
            
            elif len(foundDeck) > 3:
                embed = discord.Embed(
                    title=self.T.translate('Find.SomeDeck', lang),
                    description=self.T.translate('Find.SomeNotice', lang),
                    color=0x2b5468
                )
                
                for deck in foundDeck:
                    embed.add_field(
                        name=self.makeTitle(deck, lang),
                        value=f"{'클래스' if lang == 'KR' else 'Class'}: {deck['class']}"
                    )
                
                await ctx.send(embed=embed)
            
            else:
                await ctx.send(self.T.translate('Find.SpecificDeck', lang))
                for deck in foundDeck:
                    await ctx.send(embed=self.makeEmbed(deck, lang))
    
    async def Similar(self, ctx: commands.Context, Name: str, lang: Lang):
        await ctx.send(self.T.translate('Similar.FindFail', lang).format(Name))
        
        similar = DeckList.similar(Name)
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
        delDeck = [deck for deck in DeckList.List if deck['name'] == Name]
        
        if delDeck: # Deck found
            if not DeckList.hisCh: # history channel is not made yet
                DeckList.hisCh = self.bot.get_channel(804614670178320394)
            
            embed = self.makeEmbed(DeckList.delete(Name), lang)
            
            if SendHistory:
                await DeckList.hisCh.send(embed=embed)
            await ctx.send(self.T.translate('Delete.Success', lang).format(Name))
        
        else: # cannot find Deck
            await self.Similar(ctx, Name, lang)
    
    # ----- Command -----
    # Deck Finder
    
    @commands.command(
        name='덱검색',
        brief='덱을 검색합니다',
        description='서버에서 덱을 검색합니다. 여러개의 검색어를 공백으로 구분해 전달할 수 있습니다.',
        usage='!덱검색 (검색어)'
    )
    async def RG_Find_KR(self, ctx: commands.Context, *scThings: str):
        await self.Find(ctx, scThings, 'KR')
    
    @commands.command(
        name='search', aliases=['sc'],
        brief='Search Deck',
        description='Search Deck in server. You can search two or more words separated by spaces',
        usage='!search (search words)'
    )
    async def RG_Find_EN(self, ctx: commands.Context, *scThings: str):
        await self.Find(ctx, scThings, 'EN')
    
    # Deck Deleter
    
    @commands.command(
        name='덱삭제',
        brief='덱을 삭제합니다',
        description='덱을 삭제합니다. 해당 덱을 업로드하신 분만 삭제하실 수 있습니다. 처음 등록한 이름을 정확히 적어주셔야 합니다.',
        usage='!덱삭제 (덱 이름)'
    )
    async def RG_Delete_KR(self, ctx: commands.Context, Name: str='', SendHistory:bool=True):
        await self.Delete(ctx, Name, SendHistory, 'KR')
    
    @commands.command(
        name='delete', aliases=['remove', 'del', 'rem'],
        brief='Delete Deck',
        description='Delete Deck in Server. The deck can only be deleted by it\'s uploader. You must write exact name',
        usage='!delete (Deck name)'
    )
    async def RG_Delete_EN(self, ctx: commands.Context, Name: str='', SendHistory:bool=True):
        await self.Delete(ctx, Name, SendHistory, 'EN')
    
    # Deck Analyzer
    
    @commands.command(
        name='덱분석',
        brief='현재 저장된 덱을 분석합니다.',
        description='현재 저장된 덱을 로테/언리, 클래스 별로 분석합니다.',
        usage='!덱분석'
    )
    async def RG_Analyze_KR(self, ctx: commands.Context):
        await ctx.send(embed=DeckList.analyze('KR'))
    
    @commands.command(
        name='analyze',
        brief='analyze stored decks',
        description='analyze stored decks by Rotation/Unlimited, Class',
        usage='!analyze'
    )
    async def RG_Analyze_EN(self, ctx: commands.Context):
        await ctx.send(embed=DeckList.analyze('EN'))
    
    @commands.command(
        name='팩이름',
        brief='이번 로테이션 팩의 이름을 설정합니다. 관리자용 명령어입니다.',
        description='이번 로테이션 팩의 이름을 설정합니다. 팩 이름을 바꿀 때마다 로테이션 덱이 모두 삭제되며 역사관에 보관됩니다. 관리자용 명령어입니다.',
        usage='!팩이름 (새 팩 이름)'
    )
    @commands.has_permissions(administrator=True)
    async def RG_Pack(self, ctx: commands.Context, newPack: str=''):
        if newPack == '':
            await ctx.send('사용법: !팩이름 (새 팩 이름)\n**주의 - 모든 로테이션 덱이 삭제됩니다**')
            return
        
        db['pack'] = newPack
        await ctx.send(f'팩 이름을 {newPack}으로 바꿨어요!')
        
        if not DeckList.hisCh:
            DeckList.hisCh = self.bot.get_channel(804614670178320394)
        
        for deck in DeckList.deleteRT():
            await DeckList.hisCh.send(embed=self.makeEmbed(deck, 'KR'))
    
    @commands.command(name="세부분석")
    async def RG_DeepAnalyze(self, ctx: commands.Context):
        deckList: List[Deck] = DeckList.List
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

    @commands.command(name="po")
    async def RG_LinkPortal(self, ctx: commands.Context, DeckCode: str):
        response = requests.get(
            'https://shadowverse-portal.com/api/v1/deck/import',
            params={'format': 'json', 'deck_code': DeckCode}
        )
        d = response.json()['data']
        if len(d['errors']) > 0:
            await ctx.send("덱 코드가 무효하거나, 잘못 입력되었습니다. 다시 입력해 주시기 바랍니다.")
            return
        
        clan, hash = d['clan'], d['hash']
        deckURL, imageURL = f'https://shadowverse-portal.com/deck/{hash}', f'https://shadowverse-portal.com/image/{hash}'

        portalEmbed = discord.Embed(title="포탈로 연결!")\
            .add_field(name='덱 코드', value=DeckCode)\
            .add_field(name='포탈 링크', value=f'[여기를 클릭해주세요!]({deckURL})')\
            .set_image(url=imageURL)
        
        await ctx.send(embed=portalEmbed)
"""