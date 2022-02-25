from Common import *

from typing import Dict, List, Literal, Tuple
import requests
from bs4 import BeautifulSoup, Tag

class Table:
    players: Dict[str, List[Tuple[str, str]]] = {}

    def __init__(self, AB: Literal['A', 'B']):
        if AB not in ['A', 'B']:
            raise ValueError("AB is neither A nor B")

        self.players = {}

        day = 'day1' if AB == 'A' else 'day2'
        bs = BeautifulSoup(requests.get("http://sko.uniqxp.com/group/" + day).text, features='html.parser')

        tBody = bs.find("tbody")

        table: Tag
        for table in tBody.find_all("tr"):
            idx: Tag
            name: Tag
            cls1: Tag
            cls2: Tag

            idx, name, cls1, cls2 = table.find_all('td')
            if idx.string == '#': continue

            cls1 = cls1.find_next('a')
            cls2 = cls2.find_next('a')
            
            self.players[name.string] = {
                (cls1.string, cls1["href"]),
                (cls2.string, cls2["href"])
            }

table = {
    'A': Table('A'),
    'B': Table('B')
}
