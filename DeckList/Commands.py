import asyncio

from .Helper import *

class CogDeckList(MyCog, name="덱"):
    """
    덱리를 저장하고 구경하는 카테고리입니다.
    Command category for storing/viewing Decklist
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
    
    # ----- __init__ -----
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.T = Translator('DeckList')
        
        self.AdminOnly = [self.RG_Pack]
        self.OwnerOnly = []
        
        self.EngCmd = [self.RG_Analyze_EN, self.RG_Delete_EN]
        self.KorCmd = [self.RG_Analyze_KR, self.RG_Delete_KR, self.RG_Pack, self.RG_DeepAnalyze]
    
    @commands.Cog.listener()
    async def on_ready(self):
        DeckList.load(self.bot)
    
    # ----- Command Helper -----
    
    async def Add(self, msg: discord.Message, Name: str, Class: str, lang: Lang):
        # TODO: Add info to `Add.Usage` - To Update that deck, remove class info
        # TODO: Add Double check
        
        chID: int = msg.channel.id
        att: List[discord.Attachment] = msg.attachments
        atr: discord.User = msg.author
        
        if chID not in [758479879418937374, 758480189503832124]:
            await msg.channel.send(self.T.translate('Add.WrongChannel', lang))
            return
        
        if len(att) != 1:
            await msg.channel.send(self.T.translate('Add.NoImage', lang))
            return
        
        if not Name:
            await msg.channel.send(self.T.translate('Add.Usage', lang))
            return
        
        if Name in [deck['name'] for deck in DeckList.List]:
            await msg.channel.send(self.T.translate('Add.UsedName', lang))
            return
        
        Class = strToClass(Class)
        
        if Class not in OrgCls:
            ls = [_cls for _cls in classes.keys() if _cls in Name] # Check if name implies class
            if len(ls) == 1:
                Class = ls[0]
            else:
                await msg.channel.send(self.T.translate('Add.WrongClass', lang))
                return
        
        deck: Deck = {
            'author': str(atr.id),
            'name'  : Name.upper(),
            'class' : Class,
            'imgURL': att[0].url,
            'rtul'  : chToRTUL(chID),
            'date'  : now().strftime('%Y/%m/%d')
        }
        
        DeckList.append(deck)
        await msg.channel.send(self.T.translate('Add.Success', lang).format(Name))
    
    async def Find(self, msg: discord.Message, lang: Lang):
        scThings = msg.content.split(' ')
        
        if not scThings:
            await msg.channel.send(self.T.translate('Find.NoWord', lang))
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
            await msg.channel.send(self.T.translate('Find.NoMatchDeck', lang))
        else:
            if len(foundDeck) > 25:
                await msg.channel.send(self.T.translate('Find.TooManyDeck', lang))
            
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
                
                await msg.channel.send(embed=embed)
            
            else:
                await msg.channel.send(self.T.translate('Find.SpecificDeck', lang))
                for deck in foundDeck:
                    await msg.channel.send(embed=self.makeEmbed(deck, lang))
    
    async def Similar(self, ctx: Union[commands.Context, discord.TextChannel], Name: str, lang: Lang):
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
        # TODO: 
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
    
    async def Update(self, msg: discord.Message, Name: str, lang: Lang):
        # TODO: Add Double check
        
        att: List[discord.Attachment] = msg.attachments
        
        upDeck = [deck for deck in DeckList.List if deck['name'] == Name]
        
        if upDeck: # Deck found
            if not DeckList.hisCh:
                DeckList.hisCh = self.bot.get_channel(804614670178320394)
            
            if len(att) != 1:
                raise ValueError
            else:
                await DeckList.hisCh.send(embed=self.makeEmbed(
                    DeckList.update(Name, att[0].url, msg.author.id), lang
                ))
                
                await msg.channel.send(self.T.translate('Update.Success', lang).format(Name))
        
        else: # cannot find deck
            await self.Similar(msg.channel, Name, lang)
    
    # ----- Events -----
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.category.id == 758478112979288095: # DeckList Category
            content = message.content
            isKR = 'KR' in [role.name for role in message.author.roles]
            lang = 'KR' if isKR else 'EN'
            
            if '/' in content:
                name, cls = content.rsplit('/', 1)
                
                await self.Add(message, name, cls, lang)
            else:
                name = content
                if name in [deck['name'] for deck in DeckList.List] and len(message.attachments) > 1:
                    await self.Update(message, name, lang)
                else:
                    await self.Find(message, lang)
        else:
            await self.Find(message, lang)
    
    # ----- Command -----
    
    # Deck Deleter
    
    @commands.command(
        name='덱삭제', aliases=['delete', 'remove', 'del', 'rem'],
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
