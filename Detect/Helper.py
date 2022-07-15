from typing import Dict, List
import random

import discord

from baseDB import DB

class Detect(DB):
    def __init__(self):
        super().__init__('DB/detect.db')
    
    def getFullDetect(self):
        """get all full-detect keyword-result map with Embed-form"""
        full = {tar: rst for tar, rst in self._runSQL("SELECT tar, rst FROM FULL_DETECT")}
        # make embed manager
        return embed
    
    def getPartDetect(self):
        """get all full-detect keyword-result map with Embed-form"""
        full = {tar: rst for tar, rst in self._runSQL("SELECT tar, rst FROM PART_DETECT")}
        # make embed manager
        return embed
    
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

detect = Detect()
