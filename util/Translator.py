'''
Simple Translator for Ringonbot

Usage
    t = Translator('PackageName')
    await ctx.send(t.translate('Class.Function.Message'))

Notice
    You should have "lang/kor.json", "lang/eng.json" file in your package
'''

from typing import Dict, Literal

import json
from functools import reduce

# Typing hint
Lang = Literal['KR', 'EN']

class Translator:
    Kor: Dict[str, str]
    Eng: Dict[str, str]
    
    def __init__(self, Name: str):
        with open(f'{Name}/lang/kor.json', 'r', encoding='UTF-8') as KorFile:
            self.Kor = json.load(KorFile)
        with open(f'{Name}/lang/eng.json', 'r', encoding='UTF-8') as EngFile:
            self.Eng = json.load(EngFile)
    
    def translate(self, string: str, lang: Lang) -> str:
        if lang == 'KR':
            return reduce(dict.get, string.split('.'), self.Kor) or (string + '.NotTranslated')
        elif lang == 'EN':
            return reduce(dict.get, string.split('.'), self.Eng) or (string + '.NotTranslated')
        else:
            return (string + '.NotTranslated')
