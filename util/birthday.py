"""Provides wrapper for `birthday` database

Typical usage example:
    print(birthdayDB.get_today('06/02'))
"""

from typing import List, Dict
import logging
from datetime import datetime

from pytion import ID, parser
from pytion import Database, Parser

logger = logging.getLogger(__name__)

class BirthdayDB:
    """Provides wrapper for `birthday` database

    ### Example ::
        print(birthdayDB.get_today('06/02'))
    """

    def __init__(self):
        self.inited: bool = False
        self.data: List[Dict[str, str]] = None

    def load(self):
        """Load data from notion database"""
        database = Database(dbID=ID.database.BIRTHDAY)

        self.data = database.query(
            filter=None,
            parser=Parser(id=parser.Text, date=parser.Text)
        )

    def get_today(self, now: datetime) -> List[str]:
        """get IDs for members whom birthday is today

        ### Args ::
            now (datetime.datetime):
                datetime object that refers now

        ### Returns ::
            ID of members whom birthday is today
        """

        date = now.strftime("%m/%d")

        return [_data['id'] for _data in self.data if _data['date'] == date]

birthdayDB = BirthdayDB()
