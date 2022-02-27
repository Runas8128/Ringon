#-*- coding: utf-8 -*-

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
        desc: str
        uploader: str
        
        if len(deck['desc']) != 0:
            desc = deck['desc']
        else:
            desc = '(설명 없음)' if KE == 'KR' else '(No Desc Provided)'
        
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
        embed.add_field(name="덱 설명" if KE == 'KR' else "Description", value=desc, inline=False)
        
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
        
        self.EngCmd = [self.RG_Add_EN, self.RG_Analyze_EN, self.RG_Delete_EN, self.RG_Find_EN, self.RG_Update_EN]
        self.KorCmd = [self.RG_Add_KR, self.RG_Analyze_KR, self.RG_Delete_KR, self.RG_Find_KR, self.RG_Update_KR, self.RG_Pack]
    
    @commands.Cog.listener()
    async def on_ready(self):
        DeckList.load(self.bot)
    
    # ----- Command Helper -----
    
    async def Add(self, ctx: commands.Context, Name: str, Class: str, desc: str, lang: Lang):
        chID: int = ctx.channel.id
        att: List[discord.Attachment] = ctx.message.attachments
        atr: discord.User = ctx.author
        
        if chID not in [758479879418937374, 758480189503832124]:
            await ctx.send(self.T.translate('Add.WrongChannel', lang))
            return
        
        if len(att) != 1:
            await ctx.send(self.T.translate('Add.NoImage', lang))
            return
        
        if not Name:
            await ctx.send(self.T.translate('Add.Usage', lang))
            return
        
        if Name in [deck['name'] for deck in DeckList.List]:
            await ctx.send(self.T.translate('Add.UsedName', lang))
            return
        
        Class = strToClass(Class)
        
        if Class not in OrgCls:
            ls = [_cls for _cls in classes.keys() if _cls in Name] # Check if name implies class
            if len(ls) == 1:
                desc += Class
                Class = ls[0]
            else:
                await ctx.send(self.T.translate('Add.WrongClass', lang))
                return
        
        deck: Deck = {
            'author': str(atr.id),
            'name'  : Name.upper(),
            'class' : Class,
            'desc'  : desc,
            'imgURL': att[0].url,
            'rtul'  : chToRTUL(chID),
            'date'  : now().strftime('%Y/%m/%d')
        }
        
        DeckList.append(deck)
        await ctx.send(self.T.translate('Add.Success', lang).format(Name))
    
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
    
    async def Update(self, ctx: commands.Context, Name: str, desc: str, lang: Lang):
        att: List[discord.Attachment] = ctx.message.attachments
        
        upDeck = [deck for deck in DeckList.List if deck['name'] == Name]
        
        if upDeck: # Deck found
            if not DeckList.hisCh:
                DeckList.hisCh = self.bot.get_channel(804614670178320394)
            
            if len(att) != 1:
                DeckList.upDesc(Name, desc, ctx.author.id)
                await ctx.send(self.T.translate('Update.SuccessDesc', lang).format(Name))
            else:
                await DeckList.hisCh.send(embed=self.makeEmbed(
                    DeckList.update(Name, desc, att[0].url, ctx.author.id), lang
                ))
                
                await ctx.send(self.T.translate('Update.Success', lang).format(Name))
        
        else: # cannot find deck
            await self.Similar(ctx, Name, lang)
    
    # ----- Command -----
    
    # Deck Adder
    
    @commands.command(
        name='덱추가', aliases=['덱등록'],
        brief='서버에 덱을 추가합니다.',
        description='서버에 덱을 추가합니다.',
        usage='!덱추가 (덱 이름) (클래스) (설명 - 생략 가능) `+ 덱 사진 첨부`'
    )
    async def RG_Add_KR(self, ctx: commands.Context, Name: str = '', Class: str = '', *desc: str):
        await self.Add(ctx, Name, Class, ' '.join(desc), 'KR')
    
    @commands.command(
        name='add',
        brief='Add Deck in server',
        description='Add Deck in server',
        usage='!add (deck Name) (Class) (Description - can be skiped) `+ attach deck image`')
    async def RG_Add_EN(self, ctx: commands.Context, Name: str = '', Class: str = '', *desc: str):
        await self.Add(ctx, Name, Class, ' '.join(desc), 'EN')
    
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
    
    # Deck Updater
    
    @commands.command(
        name='덱업뎃',
        brief='덱을 업데이트합니다.',
        description='덱을 업데이트합니다. 설명만 업데이트할 경우 사진은 첨부하지 않으셔도 됩니다.',
        usage='!덱업뎃 (덱 이름) (설명 - 생략 가능)'
    )
    async def RG_Update_KR(self, ctx: commands.Context, Name: str = '', *desc: str):
        await self.Update(ctx, Name, ' '.join(desc), 'KR')
    
    @commands.command(
        name='update', aliases=['up'],
        brief='Update Deck',
        description='Update Deck\'s description/image. If you update description only, you don\'t have to attach deck image',
        usage='!update (Deck name) (Description - can be skiped)'
    )
    async def RG_Update_EN(self, ctx: commands.Context, Name: str = '', *desc: str):
        await self.Update(ctx, Name, ' '.join(desc), 'EN')
    
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
