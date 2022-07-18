from typing import Tuple, Dict

import discord

class EmbedWrapper:
    """This wrapper class wraps `discord.Embed` class

    This class provides some automated field traveling

    Parameters
    ----------
    * title: :class:`str`
        - Title of wrapped embed.
    * description: :class:`str`
        -  Description of wrapped embed.
    * fields: :class:`Tuple[Tuple[str, str]]`
        - Stored fields to travel. Wrapped embed always shows 10 of them

    ."""
    def __init__(self, title: str, description: str, *fields: Tuple[str, str]):
        self.baseMsg: discord.Message = None
        self.baseEmbed = discord.Embed(title=title, description=description, color=0x72e4f3)
        self.fields = fields
        self.count = len(fields)
        self.topIndex = 0
    
    async def send(self, channel: discord.TextChannel):
        """|coro|

        Init this embed wrapper while sending it to provided channel.

        This method does:

            1. send embed to `channel`
            2. set `self.baseMsg` and add proper reactions

        This method is automatically called when assign it into `EmbedManager` class.

        Parameters
        ----------
        * channel: :class:`discord.TextChannel`
            - channel to send this embed.

        ."""
        embed: discord.Embed = self.baseEmbed.copy()
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
        """|coro|
        Update embed with updated topIndex

        This method is automatically called in `EmbedManager.proceedReaction`
        """
        embed = self.baseEmbed.copy()
        for i in range(self.topIndex, self.topIndex+10):
            embed.add_field(name=self.fields[i][0], value=self.fields[i][1])
        
        await self.baseMsg.edit(embed=self.embed)

    async def top(self):
        """|coro|
        Set embed to top.
        This method is automatically called in `EmbedManager.proceedReaction`.
        """
        self.topIndex = 0
    
    async def up(self):
        """|coro|
        Up embed fields.
        If `self.topIndex` is less than zero, set embed to top.
        This method is automatically called in `EmbedManager.proceedReaction`.
        """
        self.topIndex -= 10
        if self.topIndex < 0:
            self.topIndex = 0
    
    async def down(self):
        """|coro|
        Down embed fields.
        If `self.topIndex` is greater than `self.count - 10`, set embed to bottom.
        This method is automatically called in `EmbedManager.proceedReaction`.
        """
        self.topIndex += 10
        if self.topIndex > self.count - 10:
            self.topIndex = self.count - 10

    async def bottom(self):
        """|coro|
        Set embed to bottom.
        This method is automatically called in `EmbedManager.proceedReaction`.
        """
        self.topIndex = self.count - 10

class EmbedManager:
    """Manager of `EmbedWrapper`.
    TODO: make remover: called when add new embed for same purpose
    """
    def __init__(self):
        self.embeds: Dict[int, EmbedWrapper] = []
    
    async def make(self, embed: EmbedWrapper, channel: discord.TextChannel):
        """|coro|
        This function init `embed` and add to `self.embeds` dictionary

        Parameters
        ----------
        * embed: :class:`EmbedWrapper`
            - embed wrapper to add in manager
        * channel: :class:`discord.TextChannel`
            - channel to send embed

        ."""
        await embed.send(channel)
        self.embeds[embed.baseMsg.id] = embed
    
    async def proceedReaction(self, msgID: int, react: str):
        """|coro|
        This function check added reaction 

        Parameters
        ----------
        * msgID: :class:`int`
            - ID for message to check reaction.
            - If it's not in `self.embeds`, reject checking.
        * react: :class:`str`
            - reaction to check.
            - assume that it is string, since targets which will be checked are all string object

        Return value
        ------------
        True if checking and traveling success, False if not.

        ."""
        if msgID not in self.embeds.keys(): return False

        embed = self.embeds[msgID]
        if   react == '⏫': await embed.top()
        elif react == '🔼': await embed.up()
        elif react == '🔽': await embed.down()
        elif react == '⏬': await embed.bottom()
        else: return False

        await embed.update()
        return True

embedManager = EmbedManager()
