from typing import List
from datetime import datetime

from .baseDB import DB

class BirthdayDB(DB):
    def __init__(self):
        super().__init__("DB/birthday.db")
    
    def getToday(self, now: datetime) -> List[int]:
        """get IDs for members whom birthday is today

        Parameters
        ----------
        * now: :class:`datetime.datetime`
            - datetime object that refers to now

        ."""
        date = now.strftime("%m/%d")
        return [
            val["ID"] for val in
            self._runSQL("SELECT ID FROM BIRTHDAY WHERE date=?", date)
        ]

birthdayDB = BirthdayDB()
