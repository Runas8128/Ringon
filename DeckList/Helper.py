from typing import Union, Callable, Dict, List
import sqlite3
import shutil
from datetime import datetime

from Common import *

Deck = Dict[str, Union[str, int]]

#--------------------------------------------------------------------------------------------------
# Class

class _DeckList:
    def __init__(self):
        self.dbCon = sqlite3.connect('db/decklist.db')
    
    def _runSQL(self, query, *parameters):
        cur = self.dbCon.cursor()
        cur.execute(query, parameters)
        self.dbCon.commit()
        return cur.fetchall()
    
    def loadHistCh(self, bot: commands.Bot):
        self.hisCh: discord.TextChannel = bot.get_channel(804614670178320394)
    
    def searchDeckByID(self, id: int):
        deckInfo = self._runSQL("SELECT name, class, description, imageURL, author FROM DECKLIST WHERE ID=?", id)[0]
        contribs = self._runSQL("SELECT ContribID FROM CONTRIBUTERS WHERE DeckID=?", id)
        return (*deckInfo, contribs)
    
    def addDeck(self, name: str, clazz: str, desc: str, imageURL: str, author: int):
        self._runSQL("""
            INSERT INTO DECKLIST (name, class, description, imageURL, author)
            VALUES(?,?,?,?,?)
        """, name, clazz, desc, imageURL, author)

        deckID = self._runSQL("SELECT ID FROM DECKLIST WHERE name=?", name)[0]

    def updateDeck(self, name: str, contrib: int, imageURL: str = '', desc: str = ''):
        query = "UPDATE DECKLIST SET "
        param = []

        if imageURL == '':
            if desc == '':
                raise ValueError("이미지파일과 설명이 모두 비어있습니다!")
            
            query += "description=?"
            param.append(desc)
        else:
            query += "imageURL=?"
            param.append(imageURL)
            if desc != '':
                query += ", description=?"
                param.append(desc)
        
        query += " WHERE name=?"
        param.append(name)
        self._runSQL(query, *param)

        deckID = self._runSQL("SELECT ID FROM DECKLIST WHERE name=?", name)[0][0]
        author = self._runSQL("SELECT author FROM DECKLIST WHERE name=?", name)[0][0]
        if author != contrib and self._runSQL("SELECT * FROM CONTRIBUTERS WHERE DeckID=?", deckID) == []:
            self._runSQL("INSERT INTO CONTRIBUTERS (DeckID, ContribID) VALUES(?,?)", deckID, contrib)

    def deleteDeck(self, name: str, reqID: int):
        author = self._runSQL("SELECT author FROM DECKLIST WHERE name=?", name)[0][0]
        if author != reqID:
            raise ValueError("덱을 등록한 사람만 삭제할 수 있습니다")
        deckInfo = self._runSQL("SELECT name, author, class, description, imageURL FROM DECKLIST WHERE name=?", name)[0]
        self._runSQL("DELETE FROM DECKLIST WHERE name=?", name)
        return deckInfo

    def deleteAll(self):
        today = datetime.now().strftime("%Y%m%d")
        shutil.copy("./DB/decklist.db", f"./DB/decklist_backup_{today}.db")
        self._runSQL("DELETE FROM DECKLIST")
        self._runSQL("DELETE FROM sqlite_sequence WHERE name='DECKLIST'")
    
    def similar(self, name: str):
        return self._runSQL("SELECT name FROM DECKLIST WHERE name LIKE ?", f"%{name}%")
    
    def analyze(self):
        data = {k: v for k, v in self._runSQL("SELECT class, COUNT(*) FROM DECKLIST GROUP BY class")}
        total = sum(deck.values())

        embed = discord.Embed(
            title=f'총 {total}개 덱 분석 결과',
            color=RGColHex
        )
        for clazz in data.keys():
            embed.add_field(
                name=clazz,
                value=f"{count:2}개 (점유율: {round(data[clazz]/total*100):5.2f}%)"
            )
        return embed

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
"""