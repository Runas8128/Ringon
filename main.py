import discord
from discord.ext import commands

Debugging = False
addingDB = False

bot = commands.Bot(command_prefix='@', help_command=None, intents=discord.Intents.all(), case_insensitive=True)

try:
    if __name__ == '__main__':
        if addingDB:
            from Common import *
        else:
            bot.load_extension('CogManager')
            bot.load_extension('Debug')
            
            from Common import TOKEN
            bot.run(TOKEN)

except discord.errors.HTTPException as E:
    from os import system
    system('clear')

    sec = int(E.response.headers['Retry-After'])
    h = sec // 3600
    sec -= h * 3600
    m = sec // 60
    sec -= m * 60
    s = sec

    print(f"Retry-After: {h}h {m}m {s}s")

finally:
    from asyncio import run
    run(bot.close())