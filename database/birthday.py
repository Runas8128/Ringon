"""Provides wrapper for `birthday` database

Typical usage example:
    print(birthdayDB.get_today('06/02'))
"""

from typing import List, Dict
import logging
from datetime import datetime

from pytion import parser
from pytion import Database, Parser

from util import database

logger = logging.getLogger(__name__)

@database(logger)
class BirthdayDB:
    """Provides wrapper for `birthday` database

    ### Example ::
        print(birthdayDB.get_today('06/02'))
    """

    def __init__(self):
        self.data: Dict[str, str] = None

    def load(self):
        """Load data from notion database"""
        _database = Database(dbID="a66f05422b91471da108737db205c7c7")

        self.data = dict(_database.query(
            filter=None,
            parser=Parser(
                only_values=True,
                ID=parser.Text, date=parser.Text
            )
        ))

    def __getitem__(self, now: datetime) -> List[str]:
        """get IDs for members whom birthday is today

        ### Args ::
            now (datetime.datetime):
                datetime object that refers now

        ### Returns ::
            ID of members whom birthday is today
        """

        date = now.strftime("%m/%d")

        return [_id for _id, _date in self.data.items() if _date == date]

birthday = BirthdayDB()
