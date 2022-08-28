from typing import List
import shutil
from dataclasses import dataclass, field

import discord
from discord.ext import commands

from .myBot import MyBot
from .utils import util

from pytion import filter, parser, prop, ID
from pytion import Database, Block, Filter, Parser

@dataclass
class Deck:
    ID: int
    name: str
    clazz: str
    desc: str
    author: str
    imageURL: str
    timestamp: str
    version: int
    contrib: List[str] = field(default_factory=list)

class DeckList:
    def __init__(self):
        self.load()

    def load(self):
        self.data_db = Database(dbID=ID.database.deck.DATA)
        self.contrib_db = Database(dbID=ID.database.deck.CONTRIB)
        self.ID_block = Block(blockID=ID.block.DECK_ID)

        self.data: List[Deck] = self.data_db.query(
            filter=None,
            parser=lambda result: Deck(**Parser(
                ID=parser.Number, name=parser.Text,
                clazz=parser.Select, desc=parser.Text, author=parser.Text,
                imageURL=parser.Text, timestamp=parser.Text,
                version=parser.Number
            )(result))
        )

        self.contrib = self.contrib_db.query(
            filter=None,
            parser=Parser(DeckID=parser.Number, ContribID=parser.Text)
        )
        
        for _contrib in self.contrib:
            try:
                deckInfo = next(
                    deck for deck in self.data
                    if deck.ID == _contrib['DeckID']
                )
                deckInfo.contrib.append(_contrib['ContribID'])
            except StopIteration:
                raise ValueError(_contrib['DeckID'])
        
        self.lastID = int(self.ID_block.get_text())
    
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
        
        try:
            return next(deck for deck in self.data if deck.ID == id)
        except StopIteration:
            print('malformed data: id #', id, sep='')
            return None

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
            rst = {
                deck.ID for deck in self.data
                if any(
                    kw in deck.name or '#' + kw in deck.desc
                    for kw in query
                )
            }
        
        if clazz != None:
            tmp = {deck.ID for deck in self.data if clazz == deck.clazz}
            if rst: rst &= tmp
            else: rst = tmp
        
        if author != None:
            author = str(author.id)
            tmp = {
                deck.ID for deck in self.data
                if author == deck.author or author in deck.contrib
            }
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
        
        return name in [deck.name for deck in self.data]

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

        self.lastID += 1
        self.ID_block.update_text(str(self.lastID))

        timestamp = util.now().strftime("%Y/%m/%d")

        self.data_db.append(
            name=prop.Title(name),
            desc=prop.Text(desc),
            clazz=prop.Select(clazz),
            author=prop.Text(author),
            imageURL=prop.Text(imageURL),
            timestamp=prop.Text(timestamp),
            version=prop.Number(1),
            ID=prop.Number(self.lastID)
        )

        self.data.append(Deck(
            ID=self.lastID,
            name=name,
            clazz=clazz,
            desc=desc,
            author=author,
            imageURl=imageURL,
            timestamp=timestamp,
            version=1
        ))

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

        deckInfo = next(deck for deck in self.data if deck.name == name)
        deckInfo.imageURL = imageURL
        deckInfo.version += 1

        properties = {
            'imageURL': prop.Text(imageURL),
            'version': prop.Number(deckInfo.version + 1)
        }

        if desc != '':
            deckInfo.desc = desc
            properties['desc'] = prop.Text(desc)

        pageID = self.data_db.query(
            filter=Filter(name=filter.Text(equals=name)),
            parser=Parser(pageID=parser.PageID)
        )[0]['pageID']
        self.data_db.update(pageID=pageID, **properties)

        contObj = {'DeckID': deckInfo['ID'], 'ContribID': str(contrib)}
        if deckInfo.author != str(contrib) and contObj not in self.contrib:
            deckInfo.contrib.append(str(contrib))
            self.contrib.append(contObj)
            self.contrib_db.append(
                DeckID=prop.Number(deckInfo['ID']),
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

        deckInfo = next(deck for deck in self.data if deck.ID == deckID)

        if deckInfo.author != str(reqID):
            raise ValueError("덱을 등록한 사람만 삭제할 수 있습니다")

        pageID = self.data_db.query(
            filter=Filter(ID=filter.Number(equals=deckID)),
            parser=Parser(pageID=parser.PageID)
        )[0]['pageID']
        
        self.data.remove(deckInfo)
        self.data_db.delete(pageID)
        
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
        statistic = [deck.clazz for deck in self.data]
        classes = set(statistic)
        total = len(statistic)
        data = {clazz: statistic.count(clazz) for clazz in classes}

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
