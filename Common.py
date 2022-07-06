# --------------------------------------------------------------------------------------------------
# Module import

from typing import Any, List, Optional

from random   import choice, random
from datetime import datetime, timedelta, timezone
from time     import time
from traceback import format_exc
import re

import discord
from   discord.ext import tasks, commands

from Translator import Translator, Lang

# --------------------------------------------------------------------------------------------------
# Variables

# RT/UL
RT = '로테이션'
UL = '언리미티드'

# Others
RGColHex = 0x72e4f3

OrgCls = ['엘프', '로얄', '위치', '드래곤', '네크로맨서', '뱀파이어', '비숍', '네메시스']
OrgClsEN = ['forest', 'sword', 'rune', 'dragon', 'shadow', 'blood', 'haven', 'portal']

classes = {
    '엘프': '엘프',
    '엘': '엘프',
    'forest': '엘프',
    
    '로얄': '로얄',
    'sword': '로얄',
    
    '위치': '위치',
    'rune': '위치',
    
    '드래곤': '드래곤',
    '래곤': '드래곤',
    '용': '드래곤',
    'dragon': '드래곤',
    
    '네크로맨서': '네크로맨서',
    '네크': '네크로맨서',
    '넼': '네크로맨서',
    'shadow': '네크로맨서',
    
    '뱀파이어': '뱀파이어',
    '뱀파': '뱀파이어',
    '뱀': '뱀파이어',
    'blood': '뱀파이어',
    
    '비숍': '비숍',
    '숍': '비숍',
    'haven': '비숍',
    
    '네메시스': '네메시스',
    '네메': '네메시스',
    '넴': '네메시스',
    'portal': '네메시스'
}

#--------------------------------------------------------------------------------------------------
# Cogs

class MyCog(commands.Cog):
    bot: commands.Bot       # class' own Bot
    T: Optional[Translator] # translator - optional variable

#--------------------------------------------------------------------------------------------------
# functions

def now():
    return datetime.now(timezone(timedelta(hours=9)))

def strToClass(name: str) -> str:
    name = name.lower()
    
    if name in classes.keys():
        return classes[name]
    else:
        return name

def chToRTUL(chID: int) -> str:
    return {758479879418937374: 'RT', 758480189503832124: 'UL'}.get(chID, "RT")

def toGen(tmp: Any) -> Any:
    if isinstance(tmp, ObservedList):
        tmp = list(tmp)
        return [toGen(_Elem) for _Elem in tmp]
    elif isinstance(tmp, ObservedDict):
        tmp = dict(tmp)
        return {key: toGen(tmp[key]) for key in tmp}
    else:
        return tmp
