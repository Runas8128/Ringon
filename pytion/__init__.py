"""Simple Notion API Wrapper for python.

Supported feature list:
    Block:
        read/update block text
        read all text of block's children
    Database:
        append, query, delete, update page
        Property:
            Title, Text, Number, Select
"""

from .database import Database
from .block import Block
from .version import Version

# pylint: disable=redefined-builtin
from .db import property as prop, filter, parser
from .db.filter import Filter
from .db.parser import Parser
