"""Provides wrapper for `Decklist` database

Typical usage example:
    print(decklist.analyze())
"""

from typing import List, Dict
import shutil
import logging
from dataclasses import dataclass, field

import discord

# pylint: disable=redefined-builtin
from pytion import filter, parser, prop, ID
from pytion import Database, Block, Filter, Parser

from ringon import Ringon
from .utils import util
from .logger import loader

logger = logging.getLogger(__name__)

@dataclass
class Deck:
    """Indicate Deck object.

    ### Attributes ::
        deck_id (int): ID of deck.
        name (str): name of deck.
        clazz (str): class of deck.
        desc (str): description of deck.
        author (str): author id of deck.
        image_url (str): deck image url.
    """
    deck_id: int
    name: str
    clazz: str
    desc: str
    author: str
    image_url: str
    timestamp: str
    version: int
    contrib: List[str] = field(default_factory=list)

class DeckList:
    """Database for managing deck list.
    """
    def __init__(self):
        self.inited: bool = False
        self.history_channel: discord.TextChannel = None

        self.data_db: Database = None
        self.contrib_db: Database = None
        self.id_block: Block = None

        self.data: List[Deck] = None
        self.contrib: List[Dict[str, str]] = None
        self.last_id: int = 0

    @loader(logger)
    def load(self, bot: Ringon):
        """Load all data from database

        ### Args ::
            bot (commands.Bot):
                Readied ringon bot instance
        """
        self.data_db = Database(dbID=ID.database.deck.DATA)
        self.contrib_db = Database(dbID=ID.database.deck.CONTRIB)
        self.id_block = Block(blockID=ID.block.DECK_ID)

        self.data: List[Deck] = self.data_db.query(
            filter=None,
            parser=lambda result: Deck(**Parser(
                deck_id=parser.Number, name=parser.Text,
                clazz=parser.Select, desc=parser.Text, author=parser.Text,
                image_url=parser.Text, timestamp=parser.Text,
                version=parser.Number
            )(result))
        )

        self.contrib = self.contrib_db.query(
            filter=None,
            parser=Parser(DeckID=parser.Number, ContribID=parser.Text)
        )

        for _contrib in self.contrib:
            try:
                deck_info = next(
                    deck for deck in self.data
                    if deck.deck_id == _contrib['DeckID']
                )
                deck_info.contrib.append(_contrib['ContribID'])
            except StopIteration as exc:
                raise ValueError(_contrib['DeckID']) from exc

        self.last_id = int(self.id_block.get_text())

        if bot.is_testing:
            self.history_channel: discord.TextChannel = bot.get_channel(1004611688802287626)
        else:
            self.history_channel: discord.TextChannel = bot.get_channel(804614670178320394)

    def search_id(self, deck_id: int):
        """Search decks by ID

        Calling this function id-by-id is needed after `searchDeck` function

        ### Args ::
            deck_id (int):
                Deck ID you want to get

        ### Returns ::
            Optional[Deck]:
                Search result.
                If cannot find matching deck, then log it and return None.
        """

        try:
            return next(deck for deck in self.data if deck.deck_id == deck_id)
        except StopIteration:
            logger.warning('malformed data: id #%d', deck_id)
            return None

    def search_query(self, query: str, clazz: str, author: discord.User):
        """Search decks with one or more keywords

        ### Args ::
            query (str):
                keywords which will be used to search.
                this function will split it by space automatically.
            clazz (str):
                your class to search, None to All class
            author (discord.User):
                deck author object, None to All member

        ### Returns ::
            List[Deck]: All searched deck info.

        ### Raises ::
            ValueError
                raised when parameters are all empty.
        """

        query = query.split()
        if len(query) == 0 and clazz is None and author is None:
            raise ValueError("검색할 단어를 입력해주세요")

        rst = set()

        if len(query) > 0:
            rst = {
                deck.deck_id for deck in self.data
                if any(
                    kw in deck.name or '#' + kw in deck.desc
                    for kw in query
                )
            }

        if clazz is not None:
            tmp = {deck.deck_id for deck in self.data if clazz == deck.clazz}
            if rst:
                rst &= tmp
            else:
                rst = tmp

        if author is not None:
            author = str(author.id)
            tmp = {
                deck.deck_id for deck in self.data
                if author == deck.author or author in deck.contrib
            }
            if rst:
                rst &= tmp
            else:
                rst = tmp

        return [self.search_id(id) for id in rst]

    def has_deck(self, name: str):
        """Check if database has deck with provided name

        ### Args ::
            name (str):
                target name of finding deck

        ### Returns ::
            bool: whether database has deck with that name.
        """

        return name in [deck.name for deck in self.data]

    def add_deck(self, name: str, clazz: str, desc: str, image_url: str, author: int):
        """Add deck in database

        ### WARNING ::
           You have to check if db has deck with same name

        ### Args ::
            name (str):
                The name of deck
            clazz (str):
                The class of deck.
                It should be one of class in shadowverse.
            desc (str):
                Description of deck.
                It can be empty(`''`, Not `None`)
            image_url (str):
                Image of deck.
                It should be http-url
            author (int):
                ID of author of this deck
        """

        self.last_id += 1
        self.id_block.update_text(str(self.last_id))

        timestamp = util.now.strftime("%Y/%m/%d")

        self.data_db.append(
            name=prop.Title(name),
            desc=prop.Text(desc),
            clazz=prop.Select(clazz),
            author=prop.Text(author),
            image_url=prop.Text(image_url),
            timestamp=prop.Text(timestamp),
            version=prop.Number(1),
            deck_id=prop.Number(self.last_id)
        )

        self.data.append(Deck(
            deck_id=self.last_id,
            name=name,
            clazz=clazz,
            desc=desc,
            author=author,
            image_url=image_url,
            timestamp=timestamp,
            version=1
        ))

    def update_deck(self, name: str, contrib: int, image_url: str, desc: str = ''):
        """Update deck image or description

        This method automatically add contributor information and increase version number

        ### WARNING ::
            You have to check if db has the deck

        ### Args ::
            name (str):
                The name of deck
            contrib (int):
                ID of contributor
            image_url (str):
                Image URL of updated deck
            desc (str):
                Description of updated deck
                If empty, not update description

        ### Raises ::
            ValueError
                raised when both image_url and desc are empty
        """

        deck_info = next(deck for deck in self.data if deck.name == name)
        deck_info.image_url = image_url
        deck_info.version += 1

        properties = {
            'image_url': prop.Text(image_url),
            'version': prop.Number(deck_info.version + 1)
        }

        if desc != '':
            deck_info.desc = desc
            properties['desc'] = prop.Text(desc)

        page_id = self.data_db.query(
            filter=Filter(name=filter.Text(equals=name)),
            parser=Parser(pageID=parser.PageID)
        )[0]['pageID']
        self.data_db.update(pageID=page_id, **properties)

        contributor_object = {'DeckID': deck_info['ID'], 'ContribID': str(contrib)}
        if deck_info.author != str(contrib) and contributor_object not in self.contrib:
            deck_info.contrib.append(str(contrib))
            self.contrib.append(contributor_object)
            self.contrib_db.append(
                DeckID=prop.Number(deck_info.deck_id),
                ContribID=prop.Text(str(contrib))
            )

    def delete_deck(self, deck_id: int, req_id: int):
        """Delete deck from database

        Only uploader must be able to delete the deck.

        ### Args ::
            name (str):
                name of deck which will be deleted
            reqID (int):
                ID of member who requested to delete this deck

        ### Returns ::
            Deck: Deck info for provided id.

        ### Raises ::
            ValueError
                raised when requester is not deck author
        """

        deck_info = next(deck for deck in self.data if deck.deck_id == deck_id)

        if deck_info.author != str(req_id):
            raise ValueError("덱을 등록한 사람만 삭제할 수 있습니다")

        page_id = self.data_db.query(
            filter=Filter(deck_id=filter.Number(equals=deck_id)),
            parser=Parser(pageID=parser.PageID)
        )[0]['pageID']

        self.data.remove(deck_info)
        self.data_db.delete(page_id)

        return deck_info

    def change_pack(self, new_pack: str):
        """Delete all deck in database, and change pack name

        ### DEPRECATED ::
            I didnt added `delete all database` feature
            will be updated soon

        ### WARNING ::
            This method will delete all deck.
            Although this method make backup automatically,
            you should double check before calling this method.
        """
        shutil.copy("./DB/decklist.db", f"./DB/decklist_backup_{util.pack}.db")
        #self._runSQL("DELETE FROM DECKLIST")
        #self._runSQL("DELETE FROM sqlite_sequence WHERE name='DECKLIST'")
        util.pack = new_pack

    def analyze(self):
        """Get deck analyze report by embed object

        ### Returns ::
            discord.Embed: Analyze report embed.
        """
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
