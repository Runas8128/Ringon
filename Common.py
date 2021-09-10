#-*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------------------
# Module import

# Module import - Type Hint

from typing import Any, List, Optional, Union

# Module import - Standard Modules

from random   import choice, random
from datetime import datetime, timedelta, timezone
from time     import time
from traceback import format_exc
import re

# Hide db import To protect db
# from replit   import db
from replit.database.database import ObservedList, ObservedDict

# Module import - Discord Module
import discord
from   discord.ext import tasks, commands

import discord_slash
from discord_slash.cog_ext import cog_slash
from discord_slash.utils.manage_commands import create_option

# Module import - My module

from Translator import Translator, Lang

# --------------------------------------------------------------------------------------------------
# Variables

# bot instance: core of bot

# TypeAliases
Context = Union[commands.Context, discord_slash.SlashContext]
cmdList = List[commands.Command]

# Temporary db - to make it works in my pc
if 'db' not in globals():
    db = {'event': [], 'HelpDft': {}, 'prof': {}, 'pack': '', 'taughts': {}, 'WordBlock': [], 'decks': [], 'maxPrize': 0, 'detect': {}, 'Help': {}, 'EventQueue': []}

# Regex
reKR = re.compile(r"[ㄱ-ㅣ가-힣]")

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

maker = {
    765462304350666762: 449837429885763584,
    235088799074484224: 166179284266778624,
    831418476211863552: 739801106703712288,
    850029959153319968: 739801106703712288
}
madeDate = {
    765462304350666762: '2020-10-13',
    235088799074484224: '2016-10-11',
    831418476211863552: '2021-05-10',
    850029959153319968: '2021-07-18'
}

#--------------------------------------------------------------------------------------------------
# Cogs

class MyCog(commands.Cog):
    bot: commands.Bot       # class' own Bot
    T: Optional[Translator] # translator - optional variable

    AdminOnly: cmdList
    OwnerOnly: cmdList

    EngCmd: cmdList
    KorCmd: cmdList

#--------------------------------------------------------------------------------------------------
# functions

def now():
    return datetime.now(timezone(timedelta(hours=9)))

def isKR(s: str) -> bool:
    return reKR.search(s) is not None

def strToClass(name: str) -> str:
    name = name.lower()
    
    if name in classes.keys():
        return classes[name]
    else:
        return name

def ClassKrToEn(name: str) -> str:
    if name in OrgCls:
        return OrgClsEN[OrgCls.index(name)]
    else:
        return name

def chToRTUL(chID: int) -> str:
    return {758479879418937374: 'RT', 758480189503832124: 'UL'}.get(chID, "RT")

def fixRTUL(rtul: str) -> str:
    return {
        '로테': RT, '로테이션': RT, 'Rotation': RT, 'RT': RT,
        '언리': UL, '언리미티드': UL, 'Unlimited': UL, 'UL': UL
    }.get(rtul, rtul)

def toGen(tmp: Any) -> Any:
    if isinstance(tmp, ObservedList):
        tmp = list(tmp)
        return [toGen(_Elem) for _Elem in tmp]
    elif isinstance(tmp, ObservedDict):
        tmp = dict(tmp)
        return {key: toGen(tmp[key]) for key in tmp}
    else:
        return tmp
