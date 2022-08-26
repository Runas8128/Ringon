from typing import List
import shutil

import discord
from discord.ext import commands

from .myBot import MyBot
from .utils import util

from pytion import filter, parser, prop, ID
from pytion import Database, Block, Filter, Parser

class DeckList:
    def __init__(self):
        self.data_db = Database(dbID=ID.database.deck.data)
        self.contrib_db = Database(dbID=ID.database.deck.contrib)
        self.ID_block = Block(blockID=ID.block.deckID)
        self.ID_extractor = Parser(only_values=True, ID=parser.Number)
    
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
        * ID `int`, author `str`
        * name `str`, class `str`, description `str`
        * version `int`
        * imageURL `str`, timestamp `str`
        * contrib `List[str]`
        
        ."""

        deckInfo = self.data_db.query(
            filter=Filter(ID=filter.Number(equals=id)),
            parser=Parser(
                ID=parser.Number,
                name=parser.Text, clazz=parser.Select, desc=parser.Text, author=parser.Text,
                imageURL=parser.Text, timestamp=parser.Text, version=parser.Number
            )
        )[0]

        deckInfo['contrib'] = self.contrib_db.query(
            filter=Filter(DeckID=filter.Number(equals=id)),
            parser=Parser(ContribID=parser.Text, only_values=True)
        )

        return deckInfo
    
    def _searchDeck(self, kw: str):
        """Search decks with one keyword. Check for name/hashtag (Private use only)"""

        name = self.data_db.query(
            filter=Filter(name=filter.Text(contains=kw)),
            parser=self.ID_extractor
        )

        hashtag = self.data_db.query(
            filter=Filter(desc=filter.Text(contains='#'+kw)),
            parser=self.ID_extractor
        )

        return set(name) | set(hashtag)

    def _searchClass(self, clazz: str):
        """Search Only for provided class (Private use only)"""
        return set(self.data_db.query(
            filter=Filter(clazz=filter.Select(equals=clazz)),
            parser=self.ID_extractor
        ))
    
    def _searchAuthor(self, author: str):
        """Search only for author id (Private use only)"""
        
        author = self.data_db.query(
            filter=Filter(author=filter.Text(equals=author)),
            parser=self.ID_extractor
        )

        contrib = self.data_db.query(
            filter=Filter(ContribID=filter.Text(equals=author)),
            parser=Parser(DeckID=parser.Number, only_values=True)
        )
        
        return set(author) | set(contrib)

    def searchDeck(self, query: str, clazz: str, author: discord.User):
        """Search decks with one or more keywords
        
        Parameters
        ----------
        * query: :class:`str`
            - keywords which will be used to search.
            - this function will split it by space automatically.
        * clazz: :class:`str`
            - your class to search, None to All class
        * author: :class:`discord.User`
            - deck author object, None to All member
        
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
            tmp = self._searchAuthor(str(author.id))
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
        
        return self.data_db.query(
            filter=Filter(name=filter.Text(equals=name)),
            parser=lambda result: 1
        ) != []

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

        ID = int(self.ID_block.get_text()) + 1
        self.ID_block.update_text(str(ID))

        self.data_db.append(
            name=prop.Title(name),
            desc=prop.Text(desc),
            clazz=prop.Select(clazz),
            author=prop.Text(author),
            imageURL=prop.Text(imageURL),
            timestamp=prop.Text(util.now().strftime("%Y/%m/%d")),
            version=prop.Number(1),
            ID=prop.Number(ID)
        )

    def updateDeck(self, name: str, contrib: int, imageURL: str, desc: str = ''):
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
        * desc: :class:`str`
            - Description of updated deck
            - If empty, not update description
        
        Exceptions
        ----------
        * ValueError
            - raised when both imageURL and desc are empty

        ."""
        payload = self.data_db.query(
            filter=Filter(name=filter.Text(equals=name)),
            parser=Parser(pageID=parser.PageID, ID=parser.Number, author=parser.Text, version=parser.Number)
        )[0]

        properties = { 'imageURL': prop.Text(imageURL), 'version': prop.Number(payload['version']+1) }
        if desc != '': properties['desc'] = prop.Text(desc)

        self.data_db.update(
            pageID=payload['pageID'],
            **properties
        )
        _contrib = self.contrib_db.query(
            filter=Filter(DeckID=filter.Number(equals=payload['ID']), ContribID=filter.Text(equals=contrib)),
            parser=lambda result: 1
        )

        if payload['author'] != str(contrib) and _contrib == []:
            self.contrib_db.append(
                DeckID=prop.Number(payload['ID']),
                ContribID=prop.Text(str(contrib))
            )

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
        payload = self.data_db.query(
            filter=Filter(ID=filter.Number(equals=deckID)),
            parser=Parser(author=parser.Text, ID=parser.PageID)
        )[0]
        
        if payload['author'] != str(reqID):
            raise ValueError("덱을 등록한 사람만 삭제할 수 있습니다")
        
        deckInfo = self.searchDeckByID(deckID)
        self.data_db.delete(payload['ID'])
        
        return deckInfo

    def changePack(self, newPack: str):
        """DEPRECATED: I didnt added `delete all database` feature: will be updated soon

        Delete all deck in database, and change pack name

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
        statistic = self.data_db.query(
            filter=None,
            parser=Parser(only_values=True, clazz=parser.Select)
        )
        classes = set(statistic)
        total = len(statistic)
        data = { clazz: statistic.count(clazz) for clazz in classes }

        embed = discord.Embed(
            title=f'총 {total}개 덱 분석 결과',
            color=0x72e4f3
        )
        for clazz in classes:
            embed.add_field(
                name=clazz,
                value=f"{data[clazz]}개 (점유율: {round(data[clazz]/total*100):.2f}%)"
            )
        return embed

deckList = DeckList()
