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
        self.nowFirstLine: int = 0
        self.detectEmbedMsg: discord.Message = None
    
    def MakeEmbed(self) -> discord.Embed:
        embed = discord.Embed(
            title="제가 감지할 친구들을 전부 알려드릴게요!",
            color=RGColHex
        )
        for src in [k for k in list(self.detects.keys())[self.nowFirstLine:self.nowFirstLine+10]]:
            embed.add_field(name=src, value=self.detects[src], inline=False)

        return embed

    def Top(self) -> discord.Embed:
        self.nowFirstLine = 0
        
        return self.MakeEmbed()

    def Up(self) -> discord.Embed:
        self.nowFirstLine -= 10
        if self.nowFirstLine < 0:
            self.nowFirstLine = 0
        
        return self.MakeEmbed()

    def Down(self) -> discord.Embed:
        self.nowFirstLine += 10
        if self.nowFirstLine > len(self.detects) - 10:
            self.nowFirstLine = len(self.detects) - 10
        
        return self.MakeEmbed()

    def Bottom(self) -> discord.Embed:
        self.nowFirstLine = len(self.detects) - 10
        
        return self.MakeEmbed()

detect = Detect()