import random

from pytion import filter, parser, ID
from pytion import Database, Filter, Parser

class Detect:
    def __init__(self):
        self.load()
    
    def load(self):
        full_db = Database(dbID=ID.database.detect.full)
        self.full = full_db.query(
            filter=None,
            parser=Parser(
                target=parser.Text, result=parser.Text
            )
        )

        prob_db = Database(dbID=ID.database.detect.prob)
        self.prob = prob_db.query(
            filter=None,
            parser=Parser(
                target=parser.Text, result=parser.Text, ratio=parser.Number
            )
        )
    
    def getList(self):
        """get all full-detect keyword-result map with Embed-form"""

        _fields = {}
        for data in self.prob:
            tar, rst, ratio = data['target'], data['result'], data['ratio']
            
            if tar in _fields.keys():
                _fields[tar] += f", {rst}(가중치: {ratio})"
            else:
                _fields[tar] = f"{rst}(가중치: {ratio})"

        fields = self.full[:]
        fields.extend([(tar+" (확률적)", _fields[tar]) for tar in _fields.keys()])

        return (
            "감지 키워드 목록입니다!",
            "이 목록에 있는 키워드가 메시지의 내용과 일치하면, 해당 메시지를 보내줍니다.",
            *(fields or [("현재 감지 목록이 비어있는 것 같아요...", "...는 아마 버그일텐데...?")])
        )
    
    def getCount(self):
        """get full-detect map length + probability-based detect map length(only count keywords)"""

        return len(self.full) + len({data['target'] for data in self.prob})
    
    def tryGet(self, tar: str) -> str:
        """try to get matching result from database"""

        try:
            return next(data['result'] for data in self.full if data['target'] == tar)
        except StopIteration:
            pass

        ProbMatch = [(data['result'], data['ratio']) for data in self.prob if data['target'] == tar]
        
        if len(ProbMatch) != 0:
            rsts, ratios = zip(*ProbMatch)
            rst = random.choices(rsts, weights=ratios, k=1)
            return rst[0]
        
        return None

detect = Detect()
