from typing import List
from datetime import datetime

from pytion import ID, filter, parser
from pytion import Database, Filter, Parser

class BirthdayDB:
    def __init__(self):
        self.db = Database(dbID=ID.database.birthday)
    
    def getToday(self, now: datetime) -> List[int]:
        """get IDs for members whom birthday is today

        Parameters
        ----------
        * now: :class:`datetime.datetime`
            - datetime object that refers to now

        ."""

        date = now.strftime("%m/%d")
        return self.db.query(
            filter=Filter(date=filter.Text(equals=date)),
            parser=Parser(only_values=True, id=parser.Number)
        )

birthdayDB = BirthdayDB()
