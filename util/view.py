from typing import Tuple, Dict, List
import re

import discord

from .deckList import deckList
from .utils import util

class baseView(discord.ui.View):
    def __init__(self, prefix):
        super().__init__()

        for child in self.children:
            if not(child._provided_custom_id and child.custom_id.startswith(prefix)): continue

            id: str = child.custom_id.replace(prefix + '_', '')
            if id.startswith('btn'): setattr(self, id, child)
    
    def __getattribute__(self, name: str) -> discord.ui.Button:
        """Do nothing but calling super's same function: only for type hinting"""
        return super().__getattribute__(name)

class EmbedView(baseView):
    """View object that provides auto traveling for `discord.Embed`."""
    def __init__(self, tarInter: discord.Interaction, title: str, description: str, *fields: Tuple[str, str]):
        super().__init__('vEmbed')

        self.baseEmbed = discord.Embed(title=title, description=description, color=0x72e4f3)
        self.fields = fields
        self.count = len(fields)
        self.topIndex = 0

        if len(fields) <= 10:
            self.btnBottom.disabled = True
            self.btnDown.disabled = True
    
    def makeEmbed(self):
        embed: discord.Embed = self.baseEmbed.copy()
        for name, value in self.fields[self.topIndex:self.topIndex+10]:
            embed.add_field(name=name, value=value)
        return embed
    
    async def update(self, interaction: discord.Interaction):
        """|coro|
        Update embed with `topIndex`
        This coroutine is automatically called when button clicked"""
        
        self.btnTop.disabled    = self.topIndex == 0
        self.btnUp.disabled     = self.topIndex == 0
        self.btnBottom.disabled = self.topIndex == self.count - 10
        self.btnDown.disabled   = self.topIndex == self.count - 10

        await interaction.response.edit_message(embed=self.makeEmbed(), view=self)
    
    @discord.ui.button(label="≪ 맨 앞으로", style=discord.ButtonStyle.blurple, custom_id="vEmbed_btnTop", disabled=True)
    async def btnTop_onClicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex = 0
        await self.update(interaction)
    
    @discord.ui.button(label=" < 앞으로", style=discord.ButtonStyle.blurple, custom_id="vEmbed_btnUp", disabled=True)
    async def btnUp_onClicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex -= 10
        if self.topIndex < 0: self.topIndex = 0
        await self.update(interaction)
    
    @discord.ui.button(label="뒤로 >", style=discord.ButtonStyle.blurple, custom_id="vEmbed_btnDown")
    async def btnDown_onCliced(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex += 10
        if self.topIndex > self.count - 10: self.topIndex = self.count - 10
        await self.update(interaction)
    
    @discord.ui.button(label="맨 뒤로 ≫", style=discord.ButtonStyle.blurple, custom_id="vEmbed_btnBottom")
    async def btnBottom_onCLicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex = self.count - 10
        await self.update(interaction)

class DeckListView(baseView):
    """EmbedView for Deck Search results"""
    def __init__(self, initInter: discord.Interaction, decks: list, emojiMap: Dict[str, discord.Emoji]):
        super().__init__("vDeckList")

        self.guild = initInter.guild
        self.decks = sorted(decks, key=lambda deck: deck['ID'])
        self.emojiMap = emojiMap
        self.index = 0
        
        self.btnGoto.label = f"☰ 1 / {len(self.decks)}"
        if len(self.decks) <= 1:
            self.btnGoto.disabled = True
            self.btnNext.disabled = True
            if len(self.decks) == 0:
                self.btnGoto.label = "-"
                self.btnDelete.disabled = True
    
    def __getMention(self, id: int):
        member = self.guild.get_member(id)
        return "(정보 없음)" if member == None else member.mention

    def makeEmbed(self):
        if len(self.decks) == 0:
            return discord.Embed(
                title="검색 결과가 없습니다!",
                description="더 일반적인 / 다른 / 더 적은 키워드를 사용해보시는건 어떤가요?",
                color=0x2b5468
            )
        
        deck = self.decks[self.index]
        embed = discord.Embed(title=deck['name'], description=f"작성자: {self.__getMention(deck['author'])}", color=0x2b5468)

        embed.add_field(name="클래스", value=deck['clazz'])
        embed.add_field(name="등록일", value=deck['timestamp'])

        if deck['version'] > 1:
            embed.add_field(name="업데이트 횟수", value=deck['version'])
            if len(deck["contrib"]) > 0:
                embed.add_field(name="기여자 목록", value=', '.join([self.__getMention(id) for id in deck["contrib"]]))
        
        embed._fields[-1]['inline'] = False
        
        if deck['desc'] != '':
            embed.add_field(name="덱 설명", value=deck['desc'], inline=False)
            hashtag_list = re.findall("#(\w+)", deck['desc'])
            if len(hashtag_list) > 0:
                embed.add_field(name="해시태그", value=', '.join(['#' + tag for tag in hashtag_list]))
        
        embed.set_image(url=deck['imageURL'])
        embed.set_footer(text=f"ID: {deck['ID']}")

        return embed

    async def update(self, interaction: discord.Interaction):
        try:
            if len(self.decks) == 0:
                self.btnPrev.disabled   = True
                self.btnGoto.label      = "-"
                self.btnNext.disabled   = True
                self.btnDelete.disabled = True
            else:
                self.btnPrev.disabled   = self.index == 0
                self.btnGoto.label      = f"☰ {self.index + 1} / {len(self.decks)}"
                self.btnNext.disabled   = self.index == (len(self.decks) - 1)
            
            await interaction.response.edit_message(embed=self.makeEmbed(), view=self)
        except KeyError:
            await interaction.response.edit_message(content="덱 정보가 불완전합니다.", view=self)

    @discord.ui.button(label="< 이전 덱", style=discord.ButtonStyle.blurple, custom_id="vDeckList_btnPrev", disabled=True)
    async def btnPrev_onClicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1
        await self.update(interaction)
    
    @discord.ui.button(label="☰ 1 / -", style=discord.ButtonStyle.gray, custom_id="vDeckList_btnGoto")
    async def btnGoto_onClicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        select = discord.ui.Select(
            placeholder="덱을 골라보세요!",
            options=[
                discord.SelectOption(
                    label=deck['name'],
                    description=deck['desc'],
                    emoji=self.emojiMap[deck['clazz']],
                    value=str(idx)
                )
                for idx, deck in enumerate(self.decks)
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            self.index = int(select.values[0])
            await self.update(interaction)
        select.callback = select_callback
        
        tmpView = discord.ui.View()
        tmpView.add_item(select)

        await interaction.response.edit_message(embed=None, view=tmpView)
    
    @discord.ui.button(label="다음 덱 >", style=discord.ButtonStyle.blurple, custom_id="vDeckList_btnNext")
    async def btnNext_onClicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.decks) - 1:
            self.index += 1
        await self.update(interaction)
    
    @discord.ui.button(label="덱 삭제", style=discord.ButtonStyle.danger, custom_id="vDeckList_btnDelete")
    async def btnDelete_onClicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        await deckList.hisCh.send(embed=self.makeEmbed())
        nowDeck = self.decks.pop(self.index)
        deckList.deleteDeck(nowDeck['ID'], interaction.user.id)
        await self.update(interaction)
