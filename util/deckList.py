from typing import List
import shutil

import discord
from discord.ext import commands

from .myBot import MyBot
from .utils import util
from .baseDB import DB

class DeckList(DB):
    def __init__(self):
        super().__init__("db/decklist.db")
    
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
        Deck info for provided id. Type: :class:`Deck`(a.k.a. `sqlite3.Row`)
        * ID `int`, author `int`
        * name `str`, class `str`, description `str`
        * version `int`
        * imageURL `str`, timestamp `str`
        * contrib `List[int]`
        
        ."""
        deckInfo = dict(self._runSQL("""SELECT * FROM DECKLIST WHERE ID=?""", id)[0])
        deckInfo["contrib"] = [
            contribID
            for tp in self._runSQL("SELECT ContribID FROM CONTRIBUTORS WHERE DeckID=?", id)
            for contribID in tp
        ]
        return deckInfo
    
    def _searchDeck(self, kw: str):
        """Search decks with one keyword. Check for name/hashtag (Private use only)"""
        return set(self._runSQL("SELECT ID FROM DECKLIST WHERE name LIKE ?", f"%{kw}%"))\
            | set(self._runSQL("SELECT ID FROM DECKLIST WHERE description LIKE ?", f"%#{kw}%"))

    def _searchClass(self, clazz: str):
        """Search Only for provided class (Private use only)"""
        return set(self._runSQL("SELECT ID FROM DECKLIST WHERE class=?", clazz))
    
    def _searchAuthor(self, author: int):
        """Search only for author id (Private use only)"""
        return set(self._runSQL("""
            SELECT ID FROM DECKLIST WHERE author=?
            UNION
            SELECT DeckID FROM CONTRIBUTORS WHERE ContribID=?
        """, author))

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
        
        return [self.searchDeckByID(row['id']) for row in rst]

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
        return len(self._runSQL("SELECT * FROM DECKLIST WHERE name=?", name)) > 0

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
        self._runSQL("""
            INSERT INTO DECKLIST (name, class, description, imageURL, author)
            VALUES(?,?,?,?,?)
        """, name, clazz, desc, imageURL, author)

    def updateDeck(self, name: str, contrib: int, imageURL: str = '', desc: str = ''):
        """Update deck image or description

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
        """Delete deck from database

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
    
    def similar(self, name: str):
        """Get decks with similar names

        ... but just all deck names which has provided string :)

        Parameters
        ----------
        * name: :class:`str`
            - substring which is in deck name
        
        Return value
        ------------
        Deck names similar with provided string. Type: List[:class:`str`]

        ."""
        return [value for tp in self._runSQL("SELECT name FROM DECKLIST WHERE name LIKE ?", f"%{name}%") for value in tp]
    
    def analyze(self):
        """Get deck analyze report by embed object

        Return value
        ------------
        Analyze report. Type: :class:`discord.Embed`

        ."""
        data = {k: v for k, v in self._runSQL("SELECT class, COUNT(*) FROM DECKLIST GROUP BY class")}
        total = sum(deck.values())

        embed = discord.Embed(
            title=f'총 {total}개 덱 분석 결과',
            color=0x72e4f3
        )
        for clazz in data.keys():
            embed.add_field(
                name=clazz,
                value=f"{count:2}개 (점유율: {round(data[clazz]/total*100):5.2f}%)"
            )
        return embed

deckList = DeckList()
