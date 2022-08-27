from typing import List
from datetime import datetime

from pytion import ID, filter, parser
from pytion import Database, Filter, Parser

class BirthdayDB:
    def __init__(self):
        self.load()

    def load(self):
        db = Database(dbID=ID.database.birthday)

        self.data = db.query(
            filter=None,
            parser=Parser(id=parser.Number, date=parser.Number)
        )
    
    def getToday(self, now: datetime) -> List[int]:
        """get IDs for members whom birthday is today

        Parameters
        ----------
        * now: :class:`datetime.datetime`
            - datetime object that refers to now

        ."""

        date = now.strftime("%m/%d")

        return [_data['id'] for _data in self.data if _data['date'] == date]

birthdayDB = BirthdayDB()
