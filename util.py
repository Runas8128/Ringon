from typing import TYPE_CHECKING

from os import environ
from logging import Logger
from datetime import datetime, timedelta
import re
import json

import discord

if TYPE_CHECKING:
    from database.decklist import Deck
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
