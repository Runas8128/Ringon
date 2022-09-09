"""Util database for Ringon."""

from typing import List
import logging

from pytion import Block

from util import database

logger = logging.getLogger(__name__)

@database(logger)
class Util:
    """Util database for Ringon.

    ### Attributes ::
        block_words (list of str):
            List of loaded block words

        pack (str):
            Pack name info
    """
    def __init__(self):
        self._block_words: List[str] = []
        self.pack_block: Block
        self._pack: str = ''

    def load(self):
        """Load blocks"""
        self._block_words = Block(blockID="233288a3891f4c008504470c8fbefc88").get_text_list()
        self.pack_block = Block(blockID="b65b0b9652d04da58f960045aa01568c")
        self._pack = self.pack_block.get_text()

    @property
    def block_words(self):
        """Indicates List of loaded block words"""
        return self._block_words

    @property
    def pack(self):
        """Indicates pack name. Setter automatically update block in notion"""
        return self._pack

    @pack.setter
    def pack(self, name: str):
        self._pack = name
        self.pack_block.update_text(name)

util = Util()
