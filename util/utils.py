from typing import List
from datetime import datetime, timedelta, timezone

from .pytion import Notion, ID

class Util:
    def __init__(self, is_testing: bool):
        self.notion = Notion(is_testing=is_testing)
    
    def now(self):
        return datetime.now(tz=timezone(offset=timedelta(hours=9)))
    
    def getBlockWord(self):
        return self.notion.get_block_text_list(ID.block.word)
    
    def getPackInfo(self):
        return self.notion.get_block_text(ID.block.pack)
    
    def setPackName(self, name: str):
        self.notion.update_block_text(ID.block.pack, name)

util = Util()
