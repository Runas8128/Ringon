"""Simple ringon instance factory."""

from typing import Optional
import logging
import asyncio

import discord
from discord.ext import commands

from util import token

logger = logging.getLogger(__name__)

class CogArgs:
    def __init__(
        self, *,
        events: bool = False,
        decklist: bool = False,
        detect: bool = False,
        birthday: bool = False,
        check: bool = False,
        other: bool = False,
        debug: bool = False
    ):
        self.cog_list = []

        if events:
            self.cog_list.append('Events')
        if decklist:
            self.cog_list.append('DeckList')
        if detect:
            self.cog_list.append('Detect')
        if birthday:
            self.cog_list.append('Birthday')
        if check:
            self.cog_list.append('Check')
        if other:
            self.cog_list.append('Other')
        if debug:
            self.cog_list.append('Debug')

    @classmethod
    def all(cls):
        return cls(
            events=True,
            decklist=True, detect=True,
            birthday=True, check=True,
            other=True, debug=True
        )

class Ringon(commands.Bot):
    """Simple ringon instance factory.

    ### Attributes ::
        is_testing (bool):
            indicates if the bot instance is in testing mode.
        test_cogs (CogArgs, optional):
            indicates list of cog name to test.
            If this parameter is missing, load all cogs (pre-defined).
    """
    def __init__(self, is_testing: bool, test_cogs: Optional[CogArgs] = None):
        super().__init__(
            command_prefix='!',
            help_command=None,
            intents=discord.Intents.all(),
            case_insensitive=True
        )

        self.is_testing = token.test = is_testing

        if self.is_testing:
            self.target_guild = discord.Object(id=823359663973072957)
        else:
            self.target_guild = discord.Object(id=758478112979288094)

        self.all_cogs = (test_cogs or CogArgs.all()).cog_list

        if self.is_testing:
            self.all_cogs.append('Debug')

        logger.info("Bot init success: is testing=%s, test cogs=%s", is_testing, self.all_cogs)

    def run(self):
        """get token automatically and run bot."""
        super().run(token['discord'], log_handler=None)

    async def setup_hook(self):
        logger.info("Setup hook starts")
        app_info = await self.application_info()
        self.owner_id = app_info.owner.id

        await asyncio.gather(*[
            self._load(cog_name) for cog_name in self.all_cogs
        ])

        await self.tree.sync(guild=self.target_guild)
        logger.info("Syncing success. all loaded cogs: %s", ', '.join(self.cogs.keys()))

    async def _load(self, name: str):
        """this coroutine loads extension, ignore `NotLoaded` exception.

        This function is coroutine.

        ### Args ::
            name (str):
                indicates cog name to load
        """
        try:
            await self.load_extension('cogs.' + name)
        except commands.ExtensionAlreadyLoaded:
            logger.warning("skipping loading cog: %s: Already loaded", name)
        except Exception as exc: # pylint: disable=broad-except
            logger.error(
                "skipping loading cog: %s: Unexpected exception raised",
                name,
                exc_info=exc
            )
