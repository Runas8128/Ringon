from typing import List
import shutil

import discord
from discord.ext import commands

from . import utils
from .baseDB import DB

class DeckList(DB):
    def __init__(self):
        super().__init__("db/decklist.db")
    
    def loadHistCh(self, bot: commands.Bot):
        """Load `역사관` channel when bot is ready
        
        Parameters
        ----------
        * bot: :class:`commands.Bot`
            - Ringon bot instance
        
        ."""
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
        deckInfo = dict(self._runSQL("""SELECT * FROM DECKLIST WHERE ID=?""", id)[0])
        deckInfo["contrib"] = [
            contribID
            for tp in self._runSQL("SELECT ContribID FROM CONTRIBUTERS WHERE DeckID=?", id)
            for contribID in tp
        ]
        return deckInfo
    
    def _searchDeck(self, kw: str):
        """Search decks with one keyword
        
        This method is private use only.

        Parameters
        ----------
        * kw: :class:`str`
            - keyword which will be used to search
        
        Return value
        ------------
        Deck IDs. Type: Set[:class:`int`]

        ."""
        return set(self._runSQL("""
            SELECT ID FROM DECKLIST WHERE author=:key OR class=:key
            UNION
            SELECT ID FROM DECKLIST WHERE name LIKE :keyLike
            UNION
            SELECT DeckID FROM CONTRIBUTORS WHERE ContribID=:key
            UNION
            SELECT DeckID FROM HASHTAG WHERE tag LIKE :keyLike
        """, {"key": kw, "keyLike": f"%{kw}%"}))

    def searchDeck(self, searchKeywords: List[str]):
        """Search decks with one or more keywords
        
        Parameters
        ----------
        * searchKeywords: List[:class:`str`]
            - keywords which will be used to search
        
        Return value
        ------------
        Deck ids. Type: List[:class:`int`]

        Exceptions
        ----------
        :class:`ValueError`
            raised when keyword list is empty
        
        ."""
        if len(searchKeywords) == 0:
            raise ValueError("검색할 단어를 입력해주세요")
        
        rst = self._searchDeck(searchKeywords.pop())
        for kw in searchKeywords:
            rst &= self._searchDeck(kw)
        return [id for tp in rst for id in tp]

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
        if author != contrib and self._runSQL("SELECT * FROM CONTRIBUTERS WHERE DeckID=? and ContribID=?", deckID, contrib) == []:
            self._runSQL("INSERT INTO CONTRIBUTERS (DeckID, ContribID) VALUES(?,?)", deckID, contrib)
        self._runSQL("UPDATE DECKLIST SET version = version + 1 WHERE ID=?", deckID)

    def deleteDeck(self, name: str, reqID: int):
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
        author = self._runSQL("SELECT author FROM DECKLIST WHERE name=?", name)[0][0]
        
        if author != reqID:
            raise ValueError("덱을 등록한 사람만 삭제할 수 있습니다")
        
        deckInfo = dict(self._runSQL("SELECT * FROM DECKLIST WHERE name=?", name)[0])
        deckInfo["contrib"] = [
            contribID
            for tp in self._runSQL("SELECT ContribID FROM CONTRIBUTERS WHERE DeckID=?", id)
            for contribID in tp
        ]
        self._runSQL("DELETE FROM DECKLIST WHERE name=?", name)
        
        return deckInfo

    def deleteAll(self):
        """Delete all deck in database

        WARNING: This method will delete all deck.
        Although this method make backup automatically, you should double check before calling this method."""
        today = utils.now().strftime("%Y%m%d")
        shutil.copy("./DB/decklist.db", f"./DB/decklist_backup_{today}.db")
        self._runSQL("DELETE FROM DECKLIST")
        self._runSQL("DELETE FROM sqlite_sequence WHERE name='DECKLIST'")
    
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
