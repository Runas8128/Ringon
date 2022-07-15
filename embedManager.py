from typing import Tuple, Dict

import discord

class EmbedWrapper:
    def __init__(self, title: str, description: str, *fields: Tuple[str, str]):
        self.baseMsg: discord.Message = None
        self.baseEmbed = discord.Embed(title=title, description=description, color=0x72e4f3)
        self.fields = fields
        self.count = len(fields)
        self.topIndex = 0
    
    async def send(self, channel: discord.TextChannel):
        embed = self.baseEmbed.copy()
        for i in range(self.topIndex, self.topIndex+10):
            embed.add_field(name=self.fields[i][0], value=self.fields[i][1])
        
        self.baseMsg = await channel.send(embed=embed)

        if self.count > 10:
            await self.baseMsg.add_reaction('🔼')
            await self.baseMsg.add_reaction('🔽')
        
        if self.count > 20:
            await self.baseMsg.add_reaction('⏫')
            await self.baseMsg.add_reaction('⏬')
    
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

class EmbedManager:
    def __init__(self):
        self.embeds: Dict[int, EmbedWrapper] = []
    
    async def make(self, embed: EmbedWrapper, channel: discord.TextChannel):
        await embed.send(channel)
        self.embeds[embed.baseMsg.id] = embed
    
    async def proceedReaction(self, msgID: int, react: str):
        if msgID not in self.embeds.keys(): return

        embed = self.embeds[msgID]
        if   react == '⏫': await embed.top()
        elif react == '🔼': await embed.up()
        elif react == '🔽': await embed.down()
        elif react == '⏬': await embed.bottom()

embedManager = EmbedManager()
