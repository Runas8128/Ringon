from typing import List
from datetime import datetime, timedelta, timezone

from pytion import ID
from pytion import Block

class Util:
    def __init__(self):
        self.load()
    
    def load(self):
        self.blockWords = Block(blockID=ID.block.word).get_text_list()
        self.pack_block = Block(blockID=ID.block.pack)
    
    def now(self):
        return datetime.now(tz=timezone(offset=timedelta(hours=9)))
    
    def getBlockWord(self):
        return self.blockWords
    
    def getPackInfo(self):
        return self.pack_block.get_text()
    
    def setPackName(self, name: str):
        self.pack_block.update_text(name)

util = Util()
