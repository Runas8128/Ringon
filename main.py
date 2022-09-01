"""Main runner file for Ringon."""

from discord.utils import setup_logging

from ringon import Ringon, CogArgs

if __name__ == '__main__':
    setup_logging()
    Ringon(
        is_testing=True,
        test_cogs=CogArgs().all()
    ).run()
