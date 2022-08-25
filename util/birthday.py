from typing import List
from datetime import datetime

from pytion import ID, filter, parser
from pytion import Notion, Filter, Parser

class BirthdayDB:
    def __init__(self):
        self.notion = Notion()
    
    def getToday(self, now: datetime) -> List[int]:
        """get IDs for members whom birthday is today

        Parameters
        ----------
        * now: :class:`datetime.datetime`
            - datetime object that refers to now

        ."""

        date = now.strftime("%m/%d")
        self.notion.query_database(
            dbID=ID.database.birthday,
            filter=Filter(date=filter.Text(equals=date)),
            parser=Parser(only_values=True, id=parser.Number)
        )

birthdayDB = BirthdayDB()
