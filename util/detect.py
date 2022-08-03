import random

from .baseDB import DB

class Detect(DB):
    def __init__(self):
        super().__init__('DB/detect.db')
    
    def getFullDetect(self):
        """get all full-detect keyword-result map with Embed-form"""

        fields = self._runSQL("SELECT tar, rst FROM FULL_DETECT")

        _fields = {}
        for tar, rst, ratio in self._runSQL("SELECT tar, rst, ratio FROM PROB_DETECT"):
            if tar in fields.keys():
                _fields[tar] += f", {rst}(가중치: {ratio})"
            else:
                _fields[tar] = f"{rst}(가중치: {ratio})"
        fields.extend([(tar+" (확률적)", _fields[tar]) for tar in _fields.keys()])

        return (
            "전체 감지 키워드 목록입니다!",
            "이 목록에 있는 키워드가 메시지의 내용과 일치하면, 해당 메시지를 보내줍니다.",
            *(fields or [("현재 감지 목록이 비어있는 것 같아요...", "...는 아마 버그일텐데...?")])
        )
    
    def getFullCount(self):
        """get full-detect map length + probability-based detect map length(only count keywords)"""
        return self._runSQL("SELECT COUNT(tar) FROM FULL_DETECT")[0][0] + \
            self._runSQL("SELECT COUNT(DISTINCT tar) FROM PROB_DETECT")[0][0]
    
    def getPartDetect(self):
        """get all partial detect keyword-result map with Embed-form"""

        fields = self._runSQL("SELECT tar, rst FROM PART_DETECT")

        return (
            "일부 감지 키워드 목록입니다!",
            "이 목록에 있는 키워드가 메시지에 포함되어 있으면, 해당 메시지를 보내줍니다.",
            *(fields or [("현재 감지 목록이 비어있는 것 같아요...", "...는 아마 버그일텐데...?")])
        )
    
    def getPartCount(self):
        """get partial detect map length"""
        return self._runSQL("SELECT COUNT(tar) FROM PART_DETECT")[0][0]
    
    def tryGet(self, tar: str) -> str:
        """try to get matching result from database"""
        FullMatch = self._runSQL("SELECT rst FROM FULL_DETECT WHERE tar=?", tar)
        if len(FullMatch) > 1:
            return FullMatch[0][0]
        
        PartMatch = self._runSQL("SELECT rst FROM PART_DETECT WHERE ? LIKE %tar%", tar)
        if len(PartMatch) > 1:
            return PartMatch[0][0]
        
        ProbMatch = self._runSQL("SELECT rst, ratio FROM PROB_DETECT WHERE tar=?", tar)
        if len(ProbMatch) > 1:
            rsts, ratios = zip(*ProbMatch)
            rst = random.choices(rsts, weights=ratios, k=1)
            return rst[0]
        
        return None

detect = Detect()
