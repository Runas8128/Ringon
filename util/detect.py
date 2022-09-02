"""Database for Detecting texts"""

from typing import List, Dict
import logging
import random

from pytion import parser, ID
from pytion import Database, Parser

from .decorator import database

logger = logging.getLogger(__name__)

@database(logger)
class Detect:
    """Database for Detecting texts"""
    def __init__(self):
        self.full: List[Dict[str, str]] = []
        self.prob: List[Dict[str, str]] = []

    def load(self):
        """Load database things"""
        full_db = Database(dbID=ID.database.detect.FULL)
        self.full = full_db.query(
            filter=None,
            parser=Parser(
                target=parser.Text, result=parser.Text
            )
        )

        prob_db = Database(dbID=ID.database.detect.PROB)
        self.prob = prob_db.query(
            filter=None,
            parser=Parser(
                target=parser.Text, result=parser.Text, ratio=parser.Number
            )
        )

    def get_list(self):
        """get all full-detect keyword-result map with Embed-form

        ### Returns ::
            List[Tuple[str, str]]: detect map with embed-form
        """

        fields = []
        for data in self.full:
            tar, rst = data['target'], data['result']

            fields.append((tar, rst))

        _fields = {}
        for data in self.prob:
            tar, rst, ratio = data['target'], data['result'], data['ratio']

            if tar in _fields:
                _fields[tar] += f", {rst}(가중치: {ratio})"
            else:
                _fields[tar] = f"{rst}(가중치: {ratio})"

        fields.extend([(tar+" (확률적)", field) for tar, field in _fields.items()])

        return (
            "감지 키워드 목록입니다!",
            "이 목록에 있는 키워드가 메시지의 내용과 일치하면, 해당 메시지를 보내줍니다.",
            *(fields or [("현재 감지 목록이 비어있는 것 같아요...", "...는 아마 버그일텐데...?")])
        )

    def __len__(self):
        """get full-detect map length + probability-based detect map length
        (only count keywords)
        """

        return len(self.full) + len({data['target'] for data in self.prob})

    def __getitem__(self, tar: str) -> str:
        """try to get matching result from database"""

        try:
            return next(
                data['result'] for data in self.full
                if data['target'] == tar
            )
        except StopIteration:
            pass

        prob_mmatch = [
            (data['result'], data['ratio']) for data in self.prob
            if data['target'] == tar
        ]

        if len(prob_mmatch) != 0:
            rsts, ratios = zip(*prob_mmatch)
            rst = random.choices(rsts, weights=ratios, k=1)
            return rst[0]

        return None

detect = Detect()
