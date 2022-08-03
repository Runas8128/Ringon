from typing import Tuple, Dict, List
import re

import discord

from .deckList import deckList
from .utils import util

class EmbedView(discord.ui.View):
    """View object that provides auto traveling for `discord.Embed`."""
    def __init__(self, tarInter: discord.Interaction, title: str, description: str, *fields: Tuple[str, str]):
        super().__init__()

        self.baseEmbed = discord.Embed(title=title, description=description, color=0x72e4f3)
        self.fields = fields
        self.count = len(fields)
        self.topIndex = 0
    
    async def update(self, interaction: discord.Interaction):
        """|coro|
        Update embed with `topIndex`
        This coroutine is automatically called when button clicked"""
        embed = self.baseEmbed.copy()
        for i in range(self.topIndex, self.topIndex+10):
            embed.add_field(name=self.fields[i][0], value=self.fields[i][1])
        
        orgMsg = interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(label="≪ 맨 앞으로", style=discord.ButtonStyle.blurple)
    async def btnTop(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex = 0
        await self.update(interaction)
    
    @discord.ui.button(label=" < 앞으로", style=discord.ButtonStyle.blurple)
    async def btnUp(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex -= 10
        if self.topIndex < 0: self.topIndex = 0
        await self.update(interaction)
    
    @discord.ui.button(label="뒤로 >", style=discord.ButtonStyle.blurple)
    async def btnDown(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex += 10
        if self.topIndex > self.count - 10: self.topIndex = self.count - 10
        await self.update(interaction)
    
    @discord.ui.button(label="맨 뒤로 ≫", style=discord.ButtonStyle.blurple)
    async def btnBottom(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex = self.count - 10
        await self.update(interaction)

class DeckListView(discord.ui.View):
    """EmbedView for Deck Search results"""
    def __init__(self, initInter: discord.Interaction, *deckIDs: List):
        super().__init__()

        self.initInter = initInter
        self.deckIDs = deckIDs
        self.index = 0
    
    def __getMention(self, id: int):
        member = self.initInter.guild.get_member(id)
        return "(정보 없음)" if member == None else member.mention

    async def makeEmbed(self):
        deck = deckList.searchDeckByID(self.deckIDs[self.index])

        try:
            embed = discord.Embed(title=deck['name'], description=f"작성자: {self.__getMention(deck['author'])}", color=0x2b5468)

            embed.add_field(name="클래스", value=deck['class'])
            embed.add_field(name="등록일", value=deck['timestamp'])

            if deck['version'] > 1:
                embed.add_field(name="업데이트 횟수", value=deck['version'])
                if len(deck["contrib"]) > 0:
                    embed.add_field(name="기여자 목록", value=', '.join([self.__getMention(id) for id in deck["contrib"]]))
            
            embed._fields[-1]['inline'] = False
            
            if deck['description'] != '':
                embed.add_field(name="덱 설명", value=deck['description'], inline=False)
                hashtag_list = re.findall("#(\w+)", deck['description'])
                if len(hashtag_list) > 0:
                    embed.add_field(name="해시태그", value=', '.join(['#' + tag for tag in hashtag_list]))
            
            embed.set_image(url=deck['imageURL'])
            embed.set_footer(text=f"ID: {deck['ID']}")

            await self.initInter.response.edit_message(
                content='',
                embed=embed
            )
        
        except KeyError:
            raise ValueError("덱 정보가 불완전합니다.")
        
    @discord.ui.button(label="< 이전 덱", style=discord.ButtonStyle.blurple)
    async def btnPrev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0: self.index -= 1
        await self.makeEmbed()
    
    @discord.ui.button(label="다음 덱 >", style=discord.ButtonStyle.blurple)
    async def btnNext(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.decks) - 2: self.index += 1
        await self.makeEmbed()
