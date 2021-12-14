#-*- coding: utf-8 -*-

from typing import Union, Callable, Dict, List

from Common import *

Deck = Dict[str, Union[str, int]]

#--------------------------------------------------------------------------------------------------
# Class

class DeckList:
    def __init__(self):
        self.List: List[Deck] = toGen(db['decks'])
        
        for idx in range(len(self.List)):
            deck = self.List[idx]
            deck['class'] = strToClass(deck['class'])
        
        self.List.sort(key=lambda deck: deck['name'])
        self.List.sort(key=lambda deck: OrgCls.index(deck['class']))

        self.hisCh: discord.TextChannel = None

    def append(self, dc: Deck) -> None:
        self.List.append(dc)
        db['decks'] = self.List

    def update(self, name: str, desc: str, imgURL: str, contrib: str) -> Deck:
        deck = self.List[[deck['name'] for deck in self.List].index(name)]
        prvDeck = deck.copy()

        deck['desc'] = desc
        deck['imgURL'] = imgURL
        deck['date'] = now().strftime('%Y/%m/%d')
        
        if not deck.get('ver'):
            deck['ver'] = 2
        else:
            deck['ver'] += 1
        
        if contrib != deck['author']:
            if not deck.get('cont', None):
                deck['cont'] = [contrib]
            elif contrib not in deck['cont']:
                deck['cont'].append(contrib)

        db['decks'] = self.List

        return prvDeck
    
    def upDesc(self, name: str, desc: str, contrib: str) -> None:
        deck = self.List[[deck['name'] for deck in self.List].index(name)]
        deck['desc'] = desc

        if contrib != deck['author']:
            if not deck.get('cont'):
                deck['cont'] = [contrib]
            elif contrib not in deck['cont']:
                deck['cont'].append(contrib)

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
