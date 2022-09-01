"""Main runner file for Ringon."""

from ringon import Ringon, CogArgs

if __name__ == '__main__':
    Ringon(
        is_testing=True,
        test_cogs=CogArgs().all()
    ).run()
