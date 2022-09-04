"""Provides some View object.

This also provides `BaseView` class, which enables you to access buttons
with member variable style.
"""

from typing import Tuple, Dict, List

import discord

from database.decklist import decklist, Deck
import util

class BaseView(discord.ui.View):
    """Base class for making View class.

    This class enables you to access your button like member variable.

    It also provides type hinting with __getattribute__ function to expect
    type if not defined in class.
    """
    def __init__(self, prefix):
        super().__init__()

        for child in self.children:
            if not(
                child._provided_custom_id and
                child.custom_id.startswith(prefix)
            ):
                continue

            _id: str = child.custom_id.replace(prefix + '_', '')
            if _id.startswith('btn'):
                setattr(self, _id, child)

    def __getattribute__(self, name: str) -> discord.ui.Button:
        """Do nothing but calling super's same function: only for type hinting"""
        return super().__getattribute__(name)

class EmbedView(BaseView):
    """View object that provides auto traveling for `discord.Embed`."""
    def __init__(self, title: str, description: str, *fields: Tuple[str, str]):
        super().__init__('vEmbed')

        self.base_embed = discord.Embed(
            title=title,
            description=description,
            color=0x72e4f3
        )
        self.fields = fields
        self.count = len(fields)
        self.top_index = 0

        if len(fields) <= 10:
            self.btnBottom.disabled = True
            self.btnDown.disabled = True

    def make_embed(self):
        """serve embed for now top index."""
        embed: discord.Embed = self.base_embed.copy()
        for name, value in self.fields[self.top_index:self.top_index+10]:
            embed.add_field(name=name, value=value)
        return embed

    async def update(self, interaction: discord.Interaction):
        """|coro|
        Update embed with `topIndex`
        This coroutine is automatically called when button clicked
        """

        self.btnTop.disabled = self.top_index == 0
        self.btnUp.disabled = self.top_index == 0
        self.btnBottom.disabled = self.top_index == self.count - 10
        self.btnDown.disabled = self.top_index == self.count - 10

        await interaction.response.edit_message(
            embed=self.make_embed(),
            view=self
        )

    @discord.ui.button(
        label="≪ 맨 앞으로",
        style=discord.ButtonStyle.blurple,
        custom_id="vEmbed_btnTop",
        disabled=True
    )
    async def btn_top(
        self,
        interaction: discord.Interaction, _button: discord.ui.Button
    ):
        """Move to top of embed."""
        self.top_index = 0
        await self.update(interaction)

    @discord.ui.button(
        label=" < 앞으로",
        style=discord.ButtonStyle.blurple,
        custom_id="vEmbed_btnUp",
        disabled=True
    )
    async def btn_up(
        self,
        interaction: discord.Interaction, _button: discord.ui.Button
    ):
        """Up 10 fields of embed."""
        self.top_index -= 10
        if self.top_index < 0:
            self.top_index = 0
        await self.update(interaction)

    @discord.ui.button(
        label="뒤로 >",
        style=discord.ButtonStyle.blurple,
        custom_id="vEmbed_btnDown"
    )
    async def btn_down(
        self,
        interaction: discord.Interaction, _button: discord.ui.Button
    ):
        """Down 10 fields of embed."""
        self.top_index += 10
        if self.top_index > self.count - 10:
            self.top_index = self.count - 10
        await self.update(interaction)

    @discord.ui.button(
        label="맨 뒤로 ≫",
        style=discord.ButtonStyle.blurple,
        custom_id="vEmbed_btnBottom"
    )
    async def btn_bottom(
        self,
        interaction: discord.Interaction, _button: discord.ui.Button
    ):
        """Move to bottom of embed."""
        self.top_index = self.count - 10
        await self.update(interaction)

class DeckListView(BaseView):
    """EmbedView for Deck Search results"""
    def __init__(
        self,
        init_inter: discord.Interaction,
        decks: List[Deck],
        emoji_map: Dict[str, discord.Emoji]
    ):
        super().__init__("vDeckList")

        self.guild = init_inter.guild
        self.decks = sorted(decks, key=lambda deck: deck.deck_id)
        self.emoji_map = emoji_map
        self.index = 0

        self.btnGoto.label = f"☰ 1 / {len(self.decks)}"
        if len(self.decks) <= 1:
            self.btnGoto.disabled = True
            self.btnNext.disabled = True
            if len(self.decks) == 0:
                self.btnGoto.label = "-"
                self.btnDelete.disabled = True

    def make_embed(self):
        """serve embed for target deck."""
        if len(self.decks) == 0:
            return discord.Embed(
                title="검색 결과가 없습니다!",
                description="더 일반적인 / 다른 / 더 적은 키워드를 사용해보시는건 어떤가요?",
                color=0x2b5468
            )

        return util.build_deck_embed(self.decks[self.index], self.guild)

    async def update(self, interaction: discord.Interaction):
        """Update embed and button text"""
        try:
            if len(self.decks) == 0:
                self.btnPrev.disabled = True
                self.btnGoto.label = "-"
                self.btnNext.disabled = True
                self.btnDelete.disabled = True
            else:
                self.btnPrev.disabled = self.index == 0
                self.btnGoto.label = f"☰ {self.index + 1} / {len(self.decks)}"
                self.btnNext.disabled = self.index == (len(self.decks) - 1)

            await interaction.response.edit_message(
                embed=self.make_embed(),
                view=self
            )
        except KeyError:
            await interaction.response.edit_message(
                content="덱 정보가 불완전합니다.",
                view=self
            )

    @discord.ui.button(
        label="< 이전 덱",
        style=discord.ButtonStyle.blurple,
        custom_id="vDeckList_btnPrev",
        disabled=True
    )
    async def btn_prev(
        self,
        interaction: discord.Interaction, _button: discord.ui.Button
    ):
        """Make embed for previous deck."""
        if self.index > 0:
            self.index -= 1
        await self.update(interaction)

    @discord.ui.button(
        label="☰ 1 / -",
        style=discord.ButtonStyle.grey,
        custom_id="vDeckList_btnGoto"
    )
    async def btn_goto(
        self,
        interaction: discord.Interaction, _button: discord.ui.Button
    ):
        """Make embed for selected deck."""
        select = discord.ui.Select(
            placeholder="덱을 골라보세요!",
            options=[
                discord.SelectOption(
                    label=deck.name,
                    description=deck.desc,
                    emoji=self.emoji_map[deck.clazz],
                    value=str(idx)
                )
                for idx, deck in enumerate(self.decks)
            ]
        )

        async def select_callback(interaction: discord.Interaction):
            self.index = int(select.values[0])
            await self.update(interaction)
        select.callback = select_callback

        await interaction.response.edit_message(
            embed=None,
            view=discord.ui.View().add_item(select)
        )

    @discord.ui.button(
        label="다음 덱 >",
        style=discord.ButtonStyle.blurple,
        custom_id="vDeckList_btnNext"
    )
    async def btn_next(
        self,
        interaction: discord.Interaction, _button: discord.ui.Button
    ):
        """Make embed for next deck."""
        if self.index < len(self.decks) - 1:
            self.index += 1
        await self.update(interaction)

    @discord.ui.button(
        label="덱 삭제",
        style=discord.ButtonStyle.danger,
        custom_id="vDeckList_btnDelete"
    )
    async def btn_delete(
        self,
        interaction: discord.Interaction, _button: discord.ui.Button
    ):
        """Delete deck from database and move to next deck"""
        await decklist.history_channel.send(embed=self.make_embed())
        target = self.decks.pop(self.index)
        decklist.delete_deck(target.deck_id, interaction.user.id)
        await self.update(interaction)
