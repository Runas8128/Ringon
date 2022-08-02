from datetime import datetime, timedelta, timezone

from .baseDB import DB

class Util(DB):
    def __init__(self):
        super().__init__('db/util.db')
    
    def now(self):
        return datetime.now(tz=timezone(offset=timedelta(hours=9)))
    
    def getBlockWord(self):
        return [
            row['value'] for row in
            self._runSQL("SELECT value FROM UTIL WHERE prop='wordBlock'")
        ]
    
    def getPackInfo(self):
        result = self._runSQL("SELECT value FROM UTIL WHERE prop='pack'")
        return result[0]['value']

util = Util()
