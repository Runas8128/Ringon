from typing import Union, Callable, Dict, List
import sqlite3

from Common import *

Deck = Dict[str, Union[str, int]]

#--------------------------------------------------------------------------------------------------
# Class

class _DeckList:
    def __init__(self):
        self.dbCon = sqlite3.connect('db/decklist.db')
    
    def _runSQL(self, query, *parameters):
        cur = self.dbCon.cursor()
        cur.execute(query, parameters=parameters)
        self.dbCon.commit()
        return cur.fetchall()
    
    def loadHistCh(self, bot: commands.Bot):
        self.hisCh: discord.TextChannel = bot.get_channel(804614670178320394)

DeckList = _DeckList()

"""
class DeckList:
    @classmethod
    def load(cls, bot: commands.Bot):
        cls.List: List[Deck] = toGen(db['decks'])
        
        # Asserting logics
        for idx in range(len(cls.List)):
            deck: Deck = cls.List[idx]
            deck['class'] = strToClass(deck['class'])
            deck['author'] = deck['author']\
                .replace('<@', '')\
                .replace('!', '')\
                .replace('>', '')
        
        db['decks'] = cls.List
        
        cls.List.sort(key=lambda deck: deck['name'])
        cls.List.sort(key=lambda deck: OrgCls.index(deck['class']))
        
        # this must be called after bot is ready
        cls.hisCh: discord.TextChannel = bot.get_channel(804614670178320394)
    
    @classmethod
    def append(cls, dc: Deck) -> None:
        cls.List.append(dc)
        db['decks'] = cls.List
    
    @classmethod
    def update(cls, name: str, imgURL: str, contrib: str) -> Deck:
        deck = cls.List[[deck['name'] for deck in cls.List].index(name)]
        prvDeck = deck.copy()
        
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
        
        db['decks'] = cls.List
        
        return prvDeck
    
    @classmethod
    def find(cls, rule: Callable[[Deck], bool]) -> List[Deck]:
        return [deck for deck in cls.List if rule(deck)]
    
    @classmethod
    def delete(cls, Name: str) -> Deck:
        idx = [deck['name'] for deck in cls.List].index(Name)
        rt = cls.List.pop(idx)
        db['decks'] = cls.List
        return rt
    
    @classmethod
    def deleteRT(cls) -> List[Deck]:
        rt = [deck for deck in cls.List if deck['rtul'] == 'RT']
        cls.List = [deck for deck in cls.List if deck['rtul'] == 'UL']
        db['decks'] = cls.List
        return rt
    
    @classmethod
    def similar(cls, Name: str) -> List[Deck]:
        return [deck for deck in cls.List if Name in deck['name']]
    
    @classmethod
    def get_asdf(cls, val: int, lang: Lang) -> str:
        if lang == 'KR':
            return f'{val:2}개 (점유율: {round(val / len(cls.List) * 100, 2):5.2f}%)'
        else:
            return f'{val:2} Decks (Rate: {round(val / len(cls.List) * 100, 2):5.2f}%)'
    
    @classmethod
    def GetStat(cls, field: str, value: str, lang: Lang = 'KR') -> str:
        return cls.get_asdf(sum([deck[field] == value for deck in cls.List]), lang)
    
    @classmethod
    def GetCount(cls, _id: int, RTUL: str, lang: Lang = 'KR') -> str:
        val = sum([(deck['author'][2:-1] == str(_id) and deck['rtul'] == RTUL) for deck in cls.List])
        return cls.get_asdf(val, lang)
    
    @classmethod
    def analyze(cls, lang: Lang = 'KR') -> discord.Embed:
        embed = discord.Embed(
            title=f'총 {len(cls.List)}개 덱분석 결과' if lang == 'KR' else f'Analyze result for {len(cls.List)} Decks',
            color=0x2b5468
        )
        
        embed.add_field(
            name='로테이션' if lang == 'KR' else 'Rotation',
            value=cls.GetStat('rtul', 'RT', lang) + '\n'
        )
        embed.add_field(
            name='언리미티드' if lang == 'KR' else 'Unlimited',
            value=cls.GetStat('rtul', 'UL', lang) + '\n'
        )
        
        # Use Zero-Width space to split contents
        embed.add_field(name='​', value='​', inline=False)
        
        for cls in OrgCls:
            embed.add_field(
                name=cls,
                value=cls.GetStat('class', cls)
            )
        
        return embed
"""