#-*- coding: utf-8 -*-

from typing import Union, Callable, Dict, List

from Common import *

Deck = Dict[str, Union[str, int]]

async def strToUser(ctx: commands.Context, s: str, default: discord.Member=None, memory:List[commands.MemberConverter]=[]) -> discord.Member:
	if not memory:
		memory = [commands.MemberConverter()]
	
	try:
		return await memory[0].convert(ctx, s)
	except:
		return default

#--------------------------------------------------------------------------------------------------
# Class

class DeckList:
    def __init__(self):
        self.List: List[Deck] = toGen(db['decks'])
        self.List.sort(key=lambda deck: deck['name'])
        self.List.sort(key=lambda deck: OrgCls.index(deck['class']))

        self.hisCh: discord.TextChannel = None

    def append(self, dc: Deck) -> None:
        self.List.append(dc)
        db['decks'] = self.List

    def update(self, name: str, desc: str, imgURL: str, contrib: str) -> Deck:
        idx = [deck['name'] for deck in self.List].index(name)
        prvDeck = self.List[idx].copy()

        self.List[idx]['desc'] = desc
        self.List[idx]['imgURL'] = imgURL
        self.List[idx]['date'] = now().strftime('%Y/%m/%d')
        
        if not self.List[idx].get('ver'):
            self.List[idx]['ver'] = 2
        else:
            self.List[idx]['ver'] += 1
        
        if contrib != self.List[idx]['author']:
            if not self.List[idx].get('cont', None):
                self.List[idx]['cont'] = [contrib]
            elif contrib not in self.List[idx]['cont']:
                self.List[idx]['cont'].add(contrib)

        db['decks'] = self.List

        return prvDeck
    
    def upDesc(self, name: str, desc: str, contrib: str) -> None:
        idx = [deck['name'] for deck in self.List].index(name)
        self.List[idx]['desc'] = desc

        if contrib != self.List[idx]['author']:
            if not self.List[idx].get('cont'):
                self.List[idx]['cont'] = {contrib}
            else:
                self.List[idx]['cont'].add(contrib)

        db['decks'] = self.List

    def find(self, rule: Callable[[Deck], bool]) -> List[Deck]:
        return [deck for deck in self.List if rule(deck)]

    def delete(self, Name: str) -> Deck:
        idx = [deck['name'] for deck in self.List].index(Name)
        rt = self.List.pop(idx)
        db['decks'] = self.List
        return rt

    def deleteRT(self) -> List[Deck]:
        rt = [deck for deck in self.List if deck['rtul'] == 'RT']
        self.List = [deck for deck in self.List if deck['rtul'] == 'UL']
        db['decks'] = self.List
        return rt

    def similar(self, Name: str) -> List[Deck]:
        return [deck for deck in self.List if Name in deck['name']]
    
    def get_asdf(self, val: int, lang: Lang) -> str:
        if lang == 'KR':
            return f'{val:2}개 (점유율: {round(val / len(self.List) * 100, 2):5.2f}%)'
        else:
            return f'{val:2} Decks (Rate: {round(val / len(self.List) * 100, 2):5.2f}%)'

    def GetStat(self, field: str, value: str, lang: Lang = 'KR') -> str:
        return self.get_asdf(sum([deck[field] == value for deck in self.List]), lang)

    def GetCount(self, _id: int, RTUL: str, lang: Lang = 'KR') -> str:
        val = sum([(deck['author'][2:-1] == str(_id) and deck['rtul'] == RTUL) for deck in self.List])
        return self.get_asdf(val, lang)

    def analyze(self, lang: Lang = 'KR') -> discord.Embed:
        embed = discord.Embed(
            title=f'총 {len(self.List)}개 덱분석 결과' if lang == 'KR' else f'Analyze result for {len(self.List)} Decks',
            color=0x2b5468
        )
        
        embed.add_field(
            name='로테이션' if lang == 'KR' else 'Rotation',
            value=self.GetStat('rtul', 'RT', lang) + '\n'
        )
        embed.add_field(
            name='언리미티드' if lang == 'KR' else 'Unlimited',
            value=self.GetStat('rtul', 'UL', lang) + '\n'
        )

        # Used Zero-Width space to split contents
        embed.add_field(name='​', value='​', inline=False)

        for cls in OrgCls:
            embed.add_field(
                name=cls,
                value=self.GetStat('class', cls)
            )
            
        return embed

dList = DeckList()

#--------------------------------------------------------------------------------------------------
# helper lambdas

def makeTitle(deck: Deck, KE: Lang = 'KR') -> str:
    name = deck['name']
    ver  = '' if not deck.get('ver') else f" ver. {deck['ver']}"
    rtul = eval(deck['rtul'])
    pack = '' if deck['rtul'] == 'UL' else f", {db['pack']} {'팩' if KE == 'KR' else 'Pack'}"
    return f"""{name}{ver}({rtul}{pack})"""

def makeEmbed(deck: Deck, KE: Lang = 'KR') -> discord.Embed:
    desc = deck['desc'] if len(deck['desc']) != 0 else ('(설명 없음)' if KE == 'KR' else '(No Desc Provided)')

    embed = discord.Embed(
        title=makeTitle(deck, KE),
        color=0x2b5468
    )
    embed.add_field(name="업로더" if KE == 'KR' else "Uploader", value=f"{deck['author']}", inline=False)
    embed.add_field(name="클래스" if KE == 'KR' else "Class", value=deck['class'], inline=False)
    embed.add_field(name="덱 설명" if KE == 'KR' else "Description", value=desc, inline=False)
    
    if deck.get('date'):
        embed.add_field(name='올린 날짜' if KE == 'KR' else 'Date', value=deck['date'])
    if deck.get('cont'):
        embed.add_field(name='기여자' if KE == 'KR' else 'Contributor', value=', '.join(deck['cont']))
    
    embed.set_image(url=deck['imgURL'])

    return embed
