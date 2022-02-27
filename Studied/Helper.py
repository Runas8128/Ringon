#-*- coding: utf-8 -*-

from Common import *

from typing import Dict, List

class Studied:
    def __init__(self):
        self.taughts: Dict[str, str] = toGen(db['taughts'])
        self.nowFirstLine: int = 0
        self.StudiedEmbedMsg: discord.Message = None
    
    def rem(self, trg: str) -> None:
        del self.taughts[trg]
        db['taughts'] = self.taughts
    
    def get(self, msg: str) -> str:
        if msg not in self.taughts:
            return ''
        
        s1: str = self.taughts[msg]
        
        if s1[:4] == '100%':
            return s1[4:]
        if ';' not in s1:
            return s1
        
        s2 = s1.split(';')
        l: List[str] = []
        
        for s3 in s2:
            s4 = s3.split('%')
            for _ in range(int(s4[0])):
                l.append(s4[1])
        
        return choice(l)
    
    def MakeEmbed(self) -> discord.Embed:
        embed = discord.Embed(
            title='제가 배운걸 전부 알려드릴게요!',
            color=RGColHex
        )
        for src in [k for k in list(self.taughts.keys())[self.nowFirstLine:self.nowFirstLine+10]]:
            embed.add_field(name=src, value=self.taughts[src], inline=False)
        
        return embed
    
    def Top(self) -> discord.Embed:
        self.nowFirstLine = 0
        
        return self.MakeEmbed()
    
    def Up(self):
        self.nowFirstLine -= 10
        if self.nowFirstLine < 0:
            self.nowFirstLine = 0
        
        return self.MakeEmbed()
    
    def Down(self):
        self.nowFirstLine += 10
        if self.nowFirstLine > len(self.taughts) - 10:
            self.nowFirstLine = len(self.taughts) - 10
        
        return self.MakeEmbed()
    
    def Bottom(self):
        self.nowFirstLine = len(self.taughts) - 10
        
        return self.MakeEmbed()

studied = Studied()