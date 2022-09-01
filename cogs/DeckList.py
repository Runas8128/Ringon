from typing import Dict

import asyncio
import requests

import discord
from discord import app_commands
from discord.ext import commands

from util.decklist import deckList
from util.view import DeckListView
from ringon import Ringon

class CogDeckList(commands.Cog):
    def __init__(self, bot: Ringon):
        self.bot = bot
        self.emojiMap: Dict[str, discord.Emoji] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await deckList.load(self.bot)

        self.emojiMap = {
            '엘프': self.bot.get_emoji(1004600679433777182),
            '로얄': self.bot.get_emoji(1004600684517261422),
            '위치': self.bot.get_emoji(1004600687688163418),
            '드래곤': self.bot.get_emoji(1004600677751848961),
            '네크로맨서': self.bot.get_emoji(1004600681266675782),
            '뱀파이어': self.bot.get_emoji(1004600685985271859),
            '비숍': self.bot.get_emoji(1004600676053155860),
            '네메시스': self.bot.get_emoji(1004600682902462465),
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.category.name != "Lab":
            # This auto-add logic only deal with `Lab` category
            return

        if len(message.attachments) == 0:
            # This auto-add logic triggered when the message has at least one attachment
            return

        if message.channel.name in ["덱리커스텀_상성확인실", "unlimited", "2pick"]:
            # This auto-add Logic is not triggered in above channels
            return

        await message.add_reaction(self.emojiMap[message.channel.name])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        channel: discord.TextChannel = self.bot.get_channel(payload.channel_id)

        if not (
            isinstance(payload.emoji, (discord.Emoji, discord.PartialEmoji)) and
            payload.emoji.id == self.emojiMap[channel.name].id
        ):
            # This auto-add Logic triggered with pre-defined emoji
            return

        orgMsg = await channel.fetch_message(payload.message_id)

        if orgMsg.author != payload.member:
            # This auto-add Logic triggered when author add reaction
            return

        try:
            while True:
                name = await self.getDeckName(orgMsg)

                if deckList.has_deck(name):
                    if await self.getIfUpdate(orgMsg):
                        await self._updateDeck(orgMsg, name)
                        return
                    else:
                        continue
                else:
                    await self._addDeck(orgMsg, name)
                    return
        except asyncio.TimeoutError:
            await channel.send("시간 초과, 덱 등록을 취소합니다.")
            return

    @app_commands.command(
        name="덱검색",
        description="DB에 저장된 덱을 검색합니다."
    )
    @app_commands.describe(
        query=(
            "검색할 키워드를 입력합니다. "
            "공백을 기준으로 분리해 덱 이름이나 덱 설명에서만 검색합니다."
        ),
        clazz="검색할 클래스를 지정합니다.",
        author="검색할 덱의 작성자/기여자를 선택합니다."
    )
    @app_commands.choices(
        clazz=[
            app_commands.Choice(name="엘프", value="엘프"),
            app_commands.Choice(name="로얄", value="로얄"),
            app_commands.Choice(name="위치", value="위치"),
            app_commands.Choice(name="드래곤", value="드래곤"),
            app_commands.Choice(name="네크로맨서", value="네크로맨서"),
            app_commands.Choice(name="뱀파이어", value="뱀파이어"),
            app_commands.Choice(name="비숍", value="비숍"),
            app_commands.Choice(name="네메시스", value="네메시스")
        ]
    )
    async def cmdSearchDeck(
        self, interaction: discord.Interaction,
        query: str = None,
        clazz: str = None,
        author: discord.Member = None
    ):
        try:
            view = DeckListView(
                interaction,
                deckList.search_query(query or '', clazz, author),
                self.emojiMap
            )
            await interaction.response.send_message(
                embed=view.make_embed(),
                view=view
            )
        except ValueError as E:
            await interaction.response.send_message(E.args[0])

    @app_commands.command(
        name="덱분석",
        description="현재 등록된 덱들을 간단하게 분석해줍니다. 클래스별 덱 갯수 및 점유율을 표시합니다."
    )
    async def cmdAnalyze(
        self, interaction: discord.Interaction
    ):
        await interaction.response.send_message(embed=deckList.analyze())

    @app_commands.command(
        name="포탈링크",
        description="덱 코드를 입력하면, 그 포탈로 가는 버튼을 만들어줍니다."
    )
    @app_commands.describe(
        deck_code="포탈 링크를 만들 덱 코드입니다."
    )
    async def cmdPortalLink(
        self, interaction: discord.Interaction,
        deck_code: str
    ):
        response = requests.get(
            'https://shadowverse-portal.com/api/v1/deck/import',
            params={'format': 'json', 'deck_code': deck_code},
            timeout=60.0
        )
        d = response.json()['data']

        if len(d['errors']) > 0:
            await interaction.response.send_message(
                "덱 코드가 무효하거나, 잘못 입력되었습니다. 다시 입력해 주시기 바랍니다.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                view=discord.ui.View().add_item(
                    discord.ui.Button(
                        label="포탈 링크",
                        url=f"https://shadowverse-portal.com/deck/{d['hash']}?lang=ko"
                    )
                )
            )

    @commands.command(name="팩이름")
    @commands.has_permissions(administrator=True)
    async def cmdChangePackName(self, ctx: commands.Context, newName: str=None):
        if newName is None:
            await ctx.send("사용법: `!팩이름 (신팩 이름: 띄어쓰기 X)")
            return

        notify: discord.Message = await ctx.send(
            embed=discord.Embed(
                title=(
                    "⚠️ 이 명령어는 현재 등록된 덱리를 "
                    "모두 삭제할 수 있습니다."
                ),
                description=(
                    "사용하시려면 `확인`을 입력해주세요! "
                    "1분 후 자동으로 취소됩니다."
                ),
                color=0x2b5468
            )
        )

        try:
            def check(msg: discord.Message):
                return all([
                    msg.author == ctx.author,
                    msg.channel == ctx.channel,
                    msg.content == "확인"
                ])

            await self.bot.wait_for('message', check=check, timeout=60.0)
            deckList.change_pack(newName)
            await ctx.send("팩 이름을 {newName}로 고쳤습니다!")
        except asyncio.TimeoutError:
            await notify.edit(
                embed=discord.Embed(
                    title="⚠️ 시간 초과, 명령어 사용을 취소합니다.",
                    color=0x2b5468
                )
            )

    async def _addDeck(self, orgMsg: discord.Message, name: str):
        """front-end method for adding deck in database

        This function is coroutine.

        ### Args ::
            orgMsg (discord.Message):
                origin message to reply
            name (str):
                name of deck which will be added

        ### NOTE ::
            deck with same name should not be in database
        """
        try:
            desc = await self.getDeckDesc(orgMsg)
        except asyncio.TimeoutError:
            await orgMsg.channel.send("시간 초과, 덱 등록을 취소합니다.")
            return

        clazz = orgMsg.channel.name
        imageURL = orgMsg.attachments[0].url
        author = orgMsg.author.id

        deckList.add_deck(name, clazz, desc, imageURL, author)
        await orgMsg.reply("덱 등록을 성공적으로 마쳤습니다!", mention_author=False)

    async def _updateDeck(self, orgMsg: discord.Message, name: str):
        """front-end method for updating deck in database

        This function is coroutine.

        ### Args ::
            orgMsg (discord.Message):
                origin message to reply
            name (str):
                name of deck which will be updated

        ### NOTE ::
            deck with same name should be in database
        """
        try:
            desc = await self.getDeckDesc(orgMsg)
        except asyncio.TimeoutError:
            await orgMsg.channel.send("시간 초과, 덱 업데이트를 취소합니다.")
            return

        imageURL = '' if len(orgMsg.attachments) == 0 else orgMsg.attachments[0].url

        try:
            deckList.update_deck(name, orgMsg.author.id, imageURL, desc=desc)
            await orgMsg.reply("덱 업데이트를 성공적으로 마쳤습니다!", mention_author=False)
        except ValueError as v:
            await orgMsg.reply(str(v))

    async def getDeckName(self, orgMsg: discord.Message):
        """get deck name with origin message

        This function is coroutine.

        ### Args ::
            orgMsg (discord.Message):
                origin message to reply

        ### Returns ::
            str: got deck name

        ### Raises ::
            asyncio.TimeoutError
                raised when response is timed out (1min)

        ."""
        def check(message: discord.Message):
            return all([
                orgMsg.author == message.author,
                orgMsg.channel == message.channel
            ])

        await orgMsg.reply(embed=discord.Embed(
            title=":ledger: 덱의 이름을 입력해주세요!",
            description="시간 제한: 1분"
        ), mention_author=False)

        msgName: discord.Message = await self.bot.wait_for('message', check=check, timeout=60.0)
        return msgName.content

    async def getIfUpdate(self, orgMsg: discord.Message):
        """get boolean data whether update deck or re-input name

        This function is coroutine.

        ### Args ::
            orgMsg (discord.Message):
                origin message to reply

        ### Returns ::
            bool: if author selected update

        ### Raises ::
            asyncio.TimeoutError
                raised when response is timed out (1min)
        """

        btnUpdate = discord.ui.Button(label="업데이트", custom_id="btn_update", emoji="↩️")
        async def onClick_btnUpdate(interaction: discord.Interaction):
            await interaction.response.send_message("덱을 업데이트합니다.", ephemeral=True)
        btnUpdate.callback = onClick_btnUpdate

        btnReinput = discord.ui.Button(label="재입력", custom_id="btn_reinput", emoji="➡️")
        async def onClick_btnReinput(interaction: discord.Interaction):
            await interaction.response.send_message("덱 이름을 재입력받습니다.", ephemeral=True)
        btnReinput.callback = onClick_btnReinput

        chkView = discord.ui.View(timeout=60.0)\
            .add_item(btnUpdate)\
            .add_item(btnReinput)

        await orgMsg.reply(
            embed=discord.Embed(
                title=":pause_button: 이미 있는 덱 이름입니다!",
                description=(
                    "이름을 바꾸려면 `재입력`을, 덱을 업데이트하려면 "
                    "`업데이트`를 선택해주세요.\n시간 제한: 1분"
                )
            ),
            view=chkView,
            mention_author=False
        )

        def check(interaction: discord.Interaction):
            return all([
                orgMsg.author.id == interaction.user.id,
                interaction.data.get('custom_id') in ['btn_update', 'btn_reinput']
            ])

        chk: discord.Interaction = await self.bot.wait_for('interaction', check=check, timeout=60.0)
        return chk.data['custom_id'] == "btn_update"

    async def getDeckDesc(self, orgMsg: discord.Message):
        """get description of deck

        This function is coroutine.

        ### Args ::
            orgMsg (discord.Message):
                origin message to reply

        ### Returns ::
            str: got description

        ### Raises ::
            asyncio.TimeoutError
                raised when response is timed out (15min)
        """
        def check(message: discord.Message):
            return orgMsg.author == message.author and orgMsg.channel == message.channel

        await orgMsg.reply(embed=discord.Embed(
            title=":ledger: 덱의 설명을 입력해주세요!",
            description="시간 제한 X\n덱 설명을 생략하려면 `생략`을 입력해주세요."
        ), mention_author=False)

        msgDesc: discord.Message = await self.bot.wait_for('message', check=check)

        desc = msgDesc.content.strip()
        if desc == "생략":
            desc = ""
        return desc

async def setup(bot: Ringon):
    await bot.add_cog(CogDeckList(bot), guild=bot.target_guild)
