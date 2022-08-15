import random

from .pytion import Notion, ID, parse_richtext

class Parser:
    def __init__(
        self, *,
        target: bool = False, result: bool = False, ratio: bool = False
    ):
        self.target = target
        self.result = result
        self.ratio = ratio
    
    def __call__(self, result):
        properties = result['properties']
        data = []

        if self.target: data.append(parse_richtext(properties['target']))
        if self.result: data.append(parse_richtext(properties['result']))
        if self.ratio:  data.append(properties['ratio']['number'])
        
        if len(data) == 1: data = data[0]
        return data

class Detect:
    def __init__(self):
        self.notion = Notion()
    
    def getList(self):
        """get all full-detect keyword-result map with Embed-form"""

        full = self.notion.query_database(
            dbID=ID.database.detect.full,
            filter=None,
            parser=Parser(target=True, result=True)
        )

        prob = self.notion.query_database(
            dbID=ID.database.detect.prob,
            filter=None,
            parser=Parser(target=True, result=True, ratio=True)
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
            parser=Parser(target=True)
        ))
        prob = len(set(self.notion.query_database(
            dbID=ID.database.detect.prob,
            filter=None,
            parser=Parser(target=True)
        )))
        return full + prob
    
    def tryGet(self, tar: str) -> str:
        """try to get matching result from database"""
        FullMatch = self.notion.query_database(
            dbID=ID.database.detect.full,
            filter={
                'property': 'target',
                'rich_text': { 'equals': tar }
            },
            parser=Parser(result=True)
        )
        if len(FullMatch) > 1:
            return FullMatch[0]
        
        ProbMatch = self.notion.query_database(
            dbID=ID.database.detect.prob,
            filter={
                'property': 'target',
                'rich_text': { 'equals': tar }
            },
            parser=Parser(result=True, ratio=True)
        )
        if len(ProbMatch) > 1:
            rsts, ratios = zip(*ProbMatch)
            rst = random.choices(rsts, weights=ratios, k=1)
            return rst[0]
        
        return None

detect = Detect()
