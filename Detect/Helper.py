#-*- coding: utf-8 -*-

from typing import Dict
from Common import *

class Detect:
    def __init__(self):
        self.detects: Dict[str, str] = {
            "멈춰": "멈춰!",
            "무야호": "<:myuyaho:837932121653903371>",
            "어림": "어림도 없지 ㄹㅇㅋㅋ"
        }
    
    def MakeEmbed(self) -> discord.Embed:
        embed = discord.Embed(
            title="제가 감지할 친구들을 전부 알려드릴게요!",
            color=RGColHex
        )
        for src in self.detects.keys():
            embed.add_field(name=src, value=self.detects[src], inline=False)
        
        return embed

detect = Detect()
