from typing import Tuple

import discord

class EmbedWrapper:
    def __init__(self, embed: discord.Embed, *fields: Tuple[str, str]):
        self.baseMsg: discord.Message = None
        self.baseEmbed = embed
        self.fields = fields
        self.count = len(fields)
        self.topIndex = 0
    
    async def send(self, channel: discord.TextChannel):
        embed = self.baseEmbed.copy()
        for i in range(self.topIndex, self.topIndex+10):
            embed.add_field(name=self.fields[i][0], value=self.fields[i][1])
        
        self.baseMsg = await channel.send(embed=embed)
    
    async def update(self):
        embed = self.baseEmbed.copy()
        for i in range(self.topIndex, self.topIndex+10):
            embed.add_field(name=self.fields[i][0], value=self.fields[i][1])
        
        await self.baseMsg.edit(embed=self.embed)

    async def top(self):
        self.topIndex = 0
        await self.update()
    
    async def up(self):
        self.topIndex -= 10
        if self.topIndex < 0:
            self.topIndex = 0
        await self.update()
    
    async def down(self):
        self.topIndex += 10
        if self.topIndex > self.count - 10:
            self.topIndex = self.count - 10
        await self.update()

    async def bottom(self):
        self.topIndex = self.count - 10
        await self.update()
