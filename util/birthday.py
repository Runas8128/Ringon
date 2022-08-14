from typing import List
from datetime import datetime

from .pytion import Notion, ID

def birthdayParser(result: dict) -> int:
    properties = result['properties']
    return properties['id']['number']

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
            filter={ 'property': 'date', 'rich_text': { 'equals': date } },
            parser=birthdayParser
        )

birthdayDB = BirthdayDB()
