from typing import List
from datetime import datetime, timedelta, timezone

from pytion import ID
from pytion import Block

class Util:
    def __init__(self):
        self.blockWord = Block(blockID=ID.block.word)
        self.pack = Block(blockID=ID.block.pack)
    
    def now(self):
        return datetime.now(tz=timezone(offset=timedelta(hours=9)))
    
    def getBlockWord(self):
        return self.blockWord.get_text_list()
    
    def getPackInfo(self):
        return self.pack.get_text()
    
    def setPackName(self, name: str):
        self.pack.update_text(name)

util = Util()
