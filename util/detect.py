import random

from pytion import filter, parser, ID
from pytion import Notion, Filter, Parser

class Detect:
    def __init__(self):
        self.notion = Notion()
    
    def getList(self):
        """get all full-detect keyword-result map with Embed-form"""

        full = self.notion.query_database(
            dbID=ID.database.detect.full,
            filter=None,
            parser=Parser(
                only_values=True,
                target=parser.Text, result=parser.Text
            )
        )

        prob = self.notion.query_database(
            dbID=ID.database.detect.prob,
            filter=None,
            parser=Parser(
                only_values=True,
                target=parser.Text, result=parser.Text, ratio=parser.Number
            )
        )

        _fields = {}
        for tar, rst, ratio in prob:
            if tar in _fields.keys():
                _fields[tar] += f", {rst}(가중치: {ratio})"
            else:
                _fields[tar] = f"{rst}(가중치: {ratio})"

        fields = full
        fields.extend([(tar+" (확률적)", _fields[tar]) for tar in _fields.keys()])

        return (
            "감지 키워드 목록입니다!",
            "이 목록에 있는 키워드가 메시지의 내용과 일치하면, 해당 메시지를 보내줍니다.",
            *(fields or [("현재 감지 목록이 비어있는 것 같아요...", "...는 아마 버그일텐데...?")])
        )
    
    def getCount(self):
        """get full-detect map length + probability-based detect map length(only count keywords)"""

        full = len(self.notion.query_database(
            dbID=ID.database.detect.full,
            filter=None,
            parser=Parser(only_values=True, target=parser.Text)
        ))
        prob = len(set(self.notion.query_database(
            dbID=ID.database.detect.prob,
            filter=None,
            parser=Parser(only_values=True, target=parser.Text)
        )))
        return full + prob
    
    def tryGet(self, tar: str) -> str:
        """try to get matching result from database"""
        FullMatch = self.notion.query_database(
            dbID=ID.database.detect.full,
            filter=Filter(target=filter.Text(equals=tar)),
            parser=Parser(only_values=True, result=parser.Text)
        )
        if len(FullMatch) >= 1:
            return FullMatch[0]
        
        ProbMatch = self.notion.query_database(
            dbID=ID.database.detect.prob,
            filter=Filter(target=filter.Text(equals=tar)),
            parser=Parser(only_values=True, result=parser.Text, ratio=parser.Number)
        )
        if len(ProbMatch) >= 1:
            rsts, ratios = zip(*ProbMatch)
            rst = random.choices(rsts, weights=ratios, k=1)
            return rst[0]
        
        return None

detect = Detect()
