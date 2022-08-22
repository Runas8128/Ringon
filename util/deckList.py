from typing import List
import shutil

import discord
from discord.ext import commands

from .myBot import MyBot
from .utils import util
from .pytion import Notion, ID
from .pytion_parser import Parser, Type

class DeckList:
    def __init__(self):
        self.notion = Notion()
        self.ID_extractor = Parser(ID=Type.Number, only_values=True)
    
    def loadHistCh(self, bot: MyBot):
        """Load `역사관` channel when bot is ready
        
        Parameters
        ----------
        * bot: :class:`commands.Bot`
            - Ringon bot instance
        
        ."""
        if bot.is_testing:
            self.hisCh: discord.TextChannel = bot.get_channel(1004611688802287626)
        else:
            self.hisCh: discord.TextChannel = bot.get_channel(804614670178320394)
    
    def searchDeckByID(self, id: int):
        """Search decks by ID

        Calling this function id-by-id is needed after `searchDeck` function

        Parameters
        ----------
        * id: :class:`int`
            - Deck ID you want to get
        
        Return value
        ------------
        Deck info for provided id. Type: :class:`dict`
        * ID `int`, author `int`
        * name `str`, class `str`, description `str`
        * version `int`
        * imageURL `str`, timestamp `str`
        * contrib `List[int]`
        
        ."""

        deckInfo = self.notion.query_database(
            dbID=ID.database.deck.data,
            filter={
                'property': 'ID',
                'number': { 'equals': id }
            },
            parser=Parser(
                ID=Type.Number,
                name=Type.Text, clazz=Type.Select, desc=Type.Text, author=Type.Number,
                imageURL=Type.Text, timestamp=Type.Text, version=Type.Number
            )
        )[0]

        deckInfo['contrib'] = self.notion.query_database(
            dbID=ID.database.deck.contrib,
            filter={
                'property': 'DeckID',
                'number': { 'equals': id }
            },
            parser=Parser(ContribID=Type.Number, only_values=True)
        )

        return deckInfo
    
    def _searchDeck(self, kw: str):
        """Search decks with one keyword. Check for name/hashtag (Private use only)"""

        name = set(self.notion.query_database(
            dbID=ID.database.deck.data,
            filter={
                'property': 'name',
                'rich_text': { 'contains': kw }
            },
            parser=self.ID_extractor
        ))

        hashtag = set(self.notion.query_database(
            dbID=ID.database.deck.data,
            filter={
                'property': 'desc',
                'rich_text': { 'contains': '#' + kw }
            },
            parser=self.ID_extractor
        ))

        return name | hashtag

    def _searchClass(self, clazz: str):
        """Search Only for provided class (Private use only)"""
        return set(self.notion.query_database(
            dbID=ID.database.deck.data,
            filter={
                'property': 'class',
                'select': { 'equals': clazz }
            },
            parser=self.ID_extractor
        ))
        return set(self._runSQL("SELECT ID FROM DECKLIST WHERE class=?", clazz))
    
    def _searchAuthor(self, author: int):
        """Search only for author id (Private use only)"""
        
        author = set(self.notion.query_database(
            dbID=ID.database.deck.data,
            filter={
                'property': 'author',
                'number': { 'equals': author }
            },
            parser=self.ID_extractor
        ))

        contrib = set(self.notion.query_database(
            dbID=ID.database.deck.data,
            filter={
                'property': 'ContribID',
                'number': { 'equals': author }
            },
            parser=Parser(DeckID=Type.Number, only_values=True)
        ))
        
        return author | contrib

    def searchDeck(self, query: str, clazz: str, author: int):
        """Search decks with one or more keywords
        
        Parameters
        ----------
        * query: :class:`str`
            - keywords which will be used to search.
            - this function will split it by space automatically.
        * clazz: :class:`str`
            - your class to search, None to All class
        * author: :class:`int`
            - ID of deck author, None to All member
        
        Return value
        ------------
        Searched deck info. Type: List[:class:`Deck`]

        Exceptions
        ----------
        :class:`ValueError`
            raised when query is empty
        
        ."""

        query = query.split()
        if len(query) == 0 and clazz == None and author == None:
            raise ValueError("검색할 단어를 입력해주세요")
        
        rst = set()

        if len(query) > 0:
            rst = self._searchDeck(query.pop())
            for kw in query:
                rst |= self._searchDeck(kw)
        
        if clazz != None:
            tmp = self._searchClass(clazz)
            if rst: rst &= tmp
            else: rst = tmp
        
        if author != None:
            tmp = self._searchAuthor(author)
            if rst: rst &= tmp
            else: rst = tmp
        
        return [self.searchDeckByID(id) for id in rst]

    def hasDeck(self, name: str):
        """Check if database has deck with provided name

        Parameters
        ----------
        * name: :class:`str`
            - target name of finding deck
        
        Return value
        ------------
        This method returns whether database has deck with that name. Type: :class:`bool`

        ."""

        return sum(self.notion.query_database(
            dbID=ID.database.deck.data,
            filter=None,
            parser=lambda result: 1
        )) > 0

    def addDeck(self, name: str, clazz: str, desc: str, imageURL: str, author: int):
        """Add deck in database

        WARNING: You have to check if db has deck with same name

        Parameters
        ----------
        * name: :class:`str`
            - The name of deck
        * clazz: :class:`str`
            - The class of deck.
            - It should be one of class in shadowverse.
        * desc: :class:`str`
            - Description of deck.
            - It can be empty(`''`, Not `None`)
        * imageURL: :class:`str`
            - Image of deck.
            - It should be http-url
        * author: :class:`int`
            - ID of author of this deck
        
        ."""

        now = util.now().strftime("%Y/%m/%d")

        self.notion.add_database(
            dbID=ID.database.deck.data,
            properties={
                'name': { 'title': [{ 'text': { 'content': name } }] },
                'desc': { 'rich_text': [{ 'text': { 'content': desc } }] },
                'class': { 'select': { 'name': clazz } },
                'author': { 'number': author },
                'imageURL': { 'rich_text': [{ 'text': { 'content': iamgeURL } }] },
                'timestamp': { 'rich_text': [{ 'text': { 'content': now } }] },
                'version': { 'number': 1 }
            }
        )

    def updateDeck(self, name: str, contrib: int, imageURL: str = '', desc: str = ''):
        """DEPRECATED: I didnt added update database feature: will be updated soon
        
        Update deck image or description

        This method automatically add contributor information and increase version number

        WARNING: You have to check if db has the deck

        Parameters
        ----------
        * name: :class:`str`
            - The name of deck
        * contrib: :class:`int`
            - ID of contributor
        * imageURL: :class:`str`
            - Image URL of updated deck
            - This can be empty (`''`, not `None`)
        * desc: :class:`str`
            - Description of updated deck
            - This can be empty (`''`, not `None`)
        
        Exceptions
        ----------
        * ValueError
            - raised when both imageURL and desc are empty

        ."""
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

        deckID, author = self._runSQL("SELECT ID, author FROM DECKLIST WHERE name=?", name)[0]
        if author != contrib and self._runSQL("SELECT * FROM CONTRIBUTORS WHERE DeckID=? and ContribID=?", deckID, contrib) == []:
            self._runSQL("INSERT INTO CONTRIBUTORS (DeckID, ContribID) VALUES(?,?)", deckID, contrib)
        self._runSQL("UPDATE DECKLIST SET version = version + 1 WHERE ID=?", deckID)

    def deleteDeck(self, deckID: int, reqID: int):
        """DEPRECATED: I didnt added delete database feature: will be updated soon

        Delete deck from database

        Only uploader must be able to delete the deck.

        Parameters
        ----------
        * name: :class:`str`
            - name of deck which will be deleted
        * reqID: :class:`int`
            - ID of member who requested to delete this deck
        
        Return value
        ------------
        Deck info for provided id. Type: :class:`dict`
        * ID `int`, author `int`
        * name `str`, class `str`, description `str`
        * version `int`
        * imageURL `str`, timestamp `str`
        * contrib `List[int]`
        
        Exceptions
        ----------
        * ValueError
            - raised when requester is not deck author

        ."""
        author = self._runSQL("SELECT author FROM DECKLIST WHERE ID=?", deckID)[0][0]
        
        if author != reqID:
            raise ValueError("덱을 등록한 사람만 삭제할 수 있습니다")
        
        deckInfo = dict(self._runSQL("SELECT * FROM DECKLIST WHERE ID=?", deckID)[0])
        deckInfo["contrib"] = [
            contribID
            for tp in self._runSQL("SELECT ContribID FROM CONTRIBUTORS WHERE DeckID=?", deckID)
            for contribID in tp
        ]
        self._runSQL("DELETE FROM DECKLIST WHERE ID=?", deckID)
        
        return deckInfo

    def changePack(self, newPack: str):
        """Delete all deck in database, and change pack name

        WARNING: This method will delete all deck.
        Although this method make backup automatically, you should double check before calling this method."""
        shutil.copy("./DB/decklist.db", f"./DB/decklist_backup_{util.getPackInfo()}.db")
        self._runSQL("DELETE FROM DECKLIST")
        self._runSQL("DELETE FROM sqlite_sequence WHERE name='DECKLIST'")
        util.setPackName(newPack)
    
    def analyze(self):
        """Get deck analyze report by embed object

        Return value
        ------------
        Analyze report. Type: :class:`discord.Embed`

        ."""
        data = {k: v for k, v in self._runSQL("SELECT class, COUNT(*) FROM DECKLIST GROUP BY class")}
        total = sum(data.values())
        print(data)

        embed = discord.Embed(
            title=f'총 {total}개 덱 분석 결과',
            color=0x72e4f3
        )
        for clazz in data.keys():
            embed.add_field(
                name=clazz,
                value=f"{data[clazz]:2}개 (점유율: {round(data[clazz]/total*100):5.2f}%)"
            )
        return embed

deckList = DeckList()
