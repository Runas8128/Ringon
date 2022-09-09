"""Main runner file for Ringon."""

import logging
from discord.utils import setup_logging
from ringon import Ringon, CogArgs

if __name__ == '__main__':
    setup_logging()
    setup_logging(handler=logging.FileHandler('.log'))
    Ringon(
        is_testing=False,
        test_cogs=CogArgs().all()
    ).run()
