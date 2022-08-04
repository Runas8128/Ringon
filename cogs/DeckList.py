from typing import Dict

import asyncio
import requests
import io

import discord
from discord import app_commands
from discord.ext import commands

from util.deckList import deckList
from util.view import DeckListView
from util.myBot import MyBot

class CogDeckList(commands.Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.emojiMap: Dict[str, discord.Emoji] = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        deckList.loadHistCh(self.bot)

        self.emojiMap = {
            '엘프':         self.bot.get_emoji(1004600679433777182),
            '로얄':         self.bot.get_emoji(1004600684517261422),
            '위치':         self.bot.get_emoji(1004600687688163418),
            '드래곤':       self.bot.get_emoji(1004600677751848961),
            '네크로맨서':   self.bot.get_emoji(1004600681266675782),
            '뱀파이어':     self.bot.get_emoji(1004600685985271859),
            '비숍':         self.bot.get_emoji(1004600676053155860),
            '네메시스':     self.bot.get_emoji(1004600682902462465),
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """ Detect all message

        If message is in `Lab` category and has attached image
            add a reaction (which is not in WMTD Server, but Bot server)
        """
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
        
        await message.add_reaction("<:Tldlr:805678671527936010>")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """ Detect all reaction even if origin message is not in cache
        
        If reaction is pre-defined emoji
            proceed deck add logic
        """

        if not (isinstance(payload.emoji, (discord.Emoji, discord.PartialEmoji)) and payload.emoji.id == 805678671527936010):
            # This auto-add Logic triggered with this emoji
            return
        
        channel: discord.TextChannel = self.bot.get_channel(payload.channel_id)
        orgMsg = await channel.fetch_message(payload.message_id)
        
        if orgMsg.author != payload.member:
            # This auto-add Logic triggered when author add reaction
            return
        
        try:
            while True:
                name = await self.getDeckName(orgMsg)

                if deckList.hasDeck(name):
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
        query="검색할 키워드를 입력합니다. 공백을 기준으로 분리해 덱 이름이나 덱 설명에서만 검색합니다.",
        clazz="검색할 클래스를 지정합니다.",
        author="검색할 덱의 작성자/기여자를 선택합니다."
    )
    @app_commands.choices(
        clazz=[
            app_commands.Choice(name="엘프",        value="엘프"),
            app_commands.Choice(name="로얄",        value="로얄"),
            app_commands.Choice(name="위치",        value="위치"),
            app_commands.Choice(name="드래곤",      value="드래곤"),
            app_commands.Choice(name="네크로맨서",  value="네크로맨서"),
            app_commands.Choice(name="뱀파이어",    value="뱀파이어"),
            app_commands.Choice(name="비숍",        value="비숍"),
            app_commands.Choice(name="네메시스",    value="네메시스")
        ]
    )
    async def cmdSearchDeck(
        self, interaction: discord.Interaction,
        query: str = None,
        clazz: str = None,
        author: discord.Member = None
    ):
        try:
            view = DeckListView(interaction, deckList.searchDeck(query or '', clazz, author), self.emojiMap)
            await interaction.response.send_message(embed=view.makeEmbed(), view=view)
        except ValueError as E:
            await interaction.response.send_message(E.args[0])
    
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
            params={'format': 'json', 'deck_code': deck_code}
        )
        d = response.json()['data']

        if len(d['errors']) > 0:
            await interaction.response.send_message("덱 코드가 무효하거나, 잘못 입력되었습니다. 다시 입력해 주시기 바랍니다.")
        else:
            await interaction.response.send_message(
                view=discord.ui.View().add_item(
                    discord.ui.Button(
                        label="포탈 링크",
                        style=discord.ButtonStyle.blurple,
                        url=f"https://shadowverse-portal.com/deck/{d['hash']}?lang=ko"
                    )
                )
            )

    @commands.command(name="팩이름")
    @commands.has_permissions(administrator=True)
    async def cmdChangePackName(self, ctx: commands.Context, newName: str=None):
        if newName == None:
            return await ctx.send("사용법: `!팩이름 (신팩 이름: 띄어쓰기 X)")
        
        notify: discord.Message = await ctx.send(
            embed=discord.Embed(
                title="⚠️ 이 명령어는 현재 등록된 덱리를 모두 삭제할 수 있습니다.",
                description="사용하시려면 `확인`을 입력해주세요! 1분 후 자동으로 취소됩니다.",
                color=0x2b5468
            )
        )

        try:
            def check(msg: discord.Message):
                return msg.author == ctx.author and msg.channel == ctx.channel and msg.content == "확인"
            
            await self.bot.wait_for('message', check=check, timeout=60.0)
            deckList.changePack(newName)
            await ctx.send("팩 이름을 {newName}로 고쳤습니다!")
        except asyncio.TimeoutError:
            await notify.edit(embed=discord.Embed(title="⚠️ 시간 초과, 명령어 사용을 취소합니다.", color=0x2b5468))

    async def _addDeck(self, orgMsg: discord.Message, name: str):
        """|coro|
        front-end method for adding deck in database

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        * name: :class:`str`
            - name of deck which will be added
            - WARNING: deck with same name should not be in database

        ."""
        try:
            desc = await self.getDeckDesc(orgMsg)
        except asyncio.TimeoutError:
            await orgMsg.channel.send("시간 초과, 덱 등록을 취소합니다.")
            return

        clazz = orgMsg.channel.name
        imageURL = orgMsg.attachments[0].url
        author = orgMsg.author.id

        deckList.addDeck(name, clazz, desc, imageURL, author)
        await orgMsg.reply("덱 등록을 성공적으로 마쳤습니다!")
    
    async def _updateDeck(self, orgMsg: discord.Message, name: str):
        """|coro|
        front-end method for updating deck in database

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        * name: :class:`str`
            - name of deck which will be updated
            - WARNING: deck with same name should be in database

        ."""
        try:
            desc = await self.getDeckDesc(orgMsg)
        except:
            await orgMsg.channel.send("시간 초과, 덱 업데이트를 취소합니다.")
            return
        
        imageURL = '' if len(orgMsg.attachments) == 0 else orgMsg.attachments[0].url
        
        try:
            deckList.updateDeck(name, orgMsg.author.id, imageURL=imageURL, desc=desc)
            await orgMsg.reply("덱 업데이트를 성공적으로 마쳤습니다!")
        except ValueError as v:
            await orgMsg.reply(str(v))

    async def getDeckName(self, orgMsg: discord.Message):
        """ get deck name with origin message

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        
        Return value
        ------------
        return got deck name

        Raises
        ------
        `asyncio.TimeoutError` when timeout(1min)

        ."""
        def check(message: discord.Message):
            return orgMsg.author == message.author and orgMsg.channel == message.channel
        
        await orgMsg.reply(embed=discord.Embed(
            title=":ledger: 덱의 이름을 입력해주세요!",
            description="시간 제한: 1분"
        ), mention_author=False)
        
        msgName: discord.Message = await self.bot.wait_for('message', check=check, timeout=60.0)
        return msgName.content
    
    async def getIfUpdate(self, orgMsg: discord.Message):
        """ get boolean data whether update deck or re-input name

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        
        Return value
        ------------
        return if author selected update

        Raises
        ------
        `asyncio.TimeoutError` when timeout(1min)

        ."""
        def check(message: discord.Message):
            return orgMsg.author == message.author and orgMsg.channel == message.channel and message.content in ["재입력", "업데이트"]
        
        await orgMsg.reply(embed=discord.Embed(
            title=":pause_button: 이미 있는 덱 이름입니다!",
            description="이름을 바꾸려면 `재입력`을, 덱을 업데이트하려면 `업데이트`를 입력해주세요.\n시간 제한: 1분"
        ), mention_author=False)
        
        msgCheck: discord.Message = await self.bot.wait_for('message', check=check, timeout=60.0)
        return msgCheck.content == "업데이트"
    
    async def getDeckDesc(self, orgMsg: discord.Message):
        """ get description of deck

        Parameters
        ----------
        * orgMsg: :class:`discord.Message`
            - origin message to reply
        
        Return value
        ------------
        return got description

        Raises
        ------
        `asyncio.TimeoutError` when timeout(15min)

        ."""
        def check(message: discord.Message):
            return orgMsg.author == message.author and orgMsg.channel == message.channel
        
        await orgMsg.reply(embed=discord.Embed(
            title=":ledger: 덱의 설명을 입력해주세요!",
            description="시간 제한: 15분\n덱 설명을 생략하려면 `생략`을 입력해주세요."
        ), mention_author=False)

        msgDesc: discord.Message = await self.bot.wait_for('message', check=check, timeout=60.0 * 15)

        desc = msgDesc.content.strip()
        if desc == "생략": desc = ""
        return desc

async def setup(bot: MyBot):
    await bot.add_cog(CogDeckList(bot), guild=bot.target_guild)

""" 
    @commands.command(name='덱분석')
    async def RG_Analyze_KR(self, ctx: commands.Context):
        await ctx.send(embed=deckList.analyze('KR'))
"""
