from typing import TYPE_CHECKING, List, Union

from os import environ
from logging import Logger
from datetime import datetime, timedelta
import re
import json
import asyncio

import discord

if TYPE_CHECKING:
    from database.decklist import Deck
    from ringon import Ringon
else:
    from collections import namedtuple
    Deck = namedtuple(
        'Deck',
        [
            'name', 'clazz', 'desc',
            'author', 'image_url',
            'timestamp', 'version',
            'contrib'
        ]
    )
    Ringon = discord.ext.commands.Bot

def database(logger: Logger):
    def deco(cls):
        class inner(cls):
            def __init__(self, *args, **kwargs):
                self.inited = False
                super().__init__(*args, **kwargs)

            def load(self):
                if self.inited:
                    logger.warning(
                        "Skipping loading module '%s': already loaded",
                        logger.name
                    )
                    return

                logger.info("Loading module '%s'", logger.name)

                try:
                    super().load()
                    self.inited = True
                    logger.info("module '%s' loaded", logger.name)
                except Exception as exc:
                    logger.error(
                        "While loading module '%s', an exception occured.",
                        logger.name, exc_info=exc
                    )
                    raise exc from None
        return inner
    return deco

class TokenProvider:
    """Generalized token loader

    If test is enabled, provider uses "/TOKEN.json" file to load token.
    Else, it uses environment variable to load token
    """
    def __init__(self):
        self.test = False
        self.load_token = self._load_deploy

    def __getitem__(self, token_key: str):
        """Token loader proxy.

        ### Returns ::
            Token value that proxy returns.
        """

        return (
            self._load_test if self.test else self._load_deploy
        )(token_key)

    def _load_test(self, token_key: str):
        """Load token from "/TOKEN.json" file.

        ### Args ::
            token_key (str):
                target key stored in "/TOKEN.json" file.

        ### Returns ::
            stored token value.

        ### Raises ::
            FileNotFoundError:
                "TOKEN.json" file is not in root directory.
            KeyError:
                Target token key is not in json file.
        """
        try:
            with open('TOKEN.json', 'r', encoding='UTF-8') as _fp:
                return json.load(_fp)[token_key]
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "[ERROR] `TOKEN.json` file is missing."
            ) from exc
        except KeyError as exc:
            raise KeyError(
                f"[ERROR] `{token_key}` field in json file is missing."
            ) from exc

    def _load_deploy(self, token_key: str):
        """Load token from environment variables.

        ### Args ::
            token_key (str):
                target key stored in environment variables.

        ### Returns ::
            stored token value.

        ### Raises ::
            KeyError:
                Target token key is not in environment variables.
        """
        try:
            return environ[token_key]
        except KeyError as exc:
            raise KeyError(
                f"[ERROR] `{token_key}` is not set in your environment variables."
            ) from exc

token = TokenProvider()

def now():
    return datetime.utcnow() + timedelta(hours=9)

def fetch_author_mention(guild: discord.Guild, _id: int):
    member = guild.get_member(_id)

    if member is None:
        return "(정보 없음)"
    else:
        return member.mention

def fetch_author_info(guild: discord.Guild, _id: str):
    member = guild.get_member(int(_id))

    if member is None:
        return {
            'name': "(정보 없음"
        }
    else:
        return {
            'name': member.display_name,
            'icon_url': member.display_avatar.url
        }

def build_deck_embed(deck: Deck, guild: discord.Guild):
    embed = discord.Embed(title=deck.name, color=0x2b5468)
    embed.set_author(**fetch_author_info(guild, deck.author))

    embed.add_field(name="클래스", value=deck.clazz)
    embed.add_field(name="등록일", value=deck.timestamp)

    if deck.version > 1:
        embed.add_field(name="업데이트 횟수", value=deck.version - 1)
        if len(deck.contrib) != 0:
            embed.add_field(
                name="기여자 목록",
                value=', '.join([
                    fetch_author_mention(guild, id) for id in deck.contrib
                ])
            )

    if deck.desc != '':
        embed.add_field(name="덱 설명", value=deck.desc, inline=False)
        hashtag_list = re.findall(r"#(\w+)", deck.desc)
        if len(hashtag_list) > 0:
            embed.add_field(
                name="해시태그",
                value=', '.join(['#' + tag for tag in hashtag_list])
            )

    embed.set_image(url=deck.image_url)
    embed.set_footer(text=f"ID: {deck.deck_id}")

    return embed

async def get_by_button(
    bot: Ringon,
    origin: Union[discord.Message, discord.Interaction],
    options: List[str],
    emojis: List[str],
    *,
    timeout: float = 60.0,
    notice_msg: str = None,
    notice_embed: discord.Embed = None
) -> str:
    """get input by button

    This function is coroutine.

    ### Args ::
        bot (Ringon):
            bot instance to get response
        origin (discord.Message | discord.Interaction):
            origin message or interaction to reply
        options (List[str]):
            select options. length should be less than 10.
        emojis (List[str]):
            emoji of option. length should be equal to `options`'s.
        timeout (float):
            second to timeout. default is 60.0 (1 min)
        notice_msg (str):
            message to send with check view.
        notice_embed (discord.Embed):
            embed to send with check view.

    ### Returns ::
        Optional[str]:
            None if timeouted,
            label of clicked button if not.

    ### Raises ::
        ValueError
            raised when length of `options` is not less than 10.
        TypeError
            raised when type of `origin` is neither `discord.Message`
            nor `discord.Interaction`
    """

    if len(options) >= 10:
        raise ValueError("length of options should be less than 10")

    view = discord.ui.View(timeout=timeout)

    for label, emoji in zip(options, emojis):
        button = discord.ui.Button(label=label, emoji=emoji)
        async def on_click(interaction: discord.Interaction):
            await interaction.response.defer()
        button.callback = on_click

        view.add_item(button)

    if isinstance(origin, discord.Message):
        origin_id = origin.author.id
        await origin.reply(
            content=notice_msg,
            embed=notice_embed,
            view=view,
            mention_author=False
        )
    elif isinstance(origin, discord.Interaction):
        origin_id = origin.user.id
        await origin.followup.send(
            content=notice_msg,
            embed=notice_embed,
            view=view
        )
    else:
        raise TypeError(
            "variable `origin` should be discord.Message or discord.Interaction, "
            f"not {type(origin)}"
        )

    def check(interaction: discord.Interaction):
        return all((
            origin_id == interaction.user.id,
            interaction.data.get('label') in options
        ))

    try:
        chk: discord.Interaction = await bot.wait_for(
            'interaction', check=check, timeout=timeout
        )
        return chk.data.get('label')
    except asyncio.TimeoutError:
        return None
