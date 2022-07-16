import discord
from discord.ext.commands import Bot

addingDB = False

bot = Bot(command_prefix='!', help_command=None, intents=discord.Intents.all(), case_insensitive=True)

try:
    if __name__ == '__main__':
        if addingDB:
            from Common import *
        else:
            bot.load_extension('util.CogManager')
            bot.load_extension('util.Debug')
            
            # code to make this bot keep alive
            # TODO: Un-comment below code
            #import keep_alive

            # code to get TOKEN value from environment values
            # TODO: Un-comment below codes
            #from os import environ
            #TOKEN = environ['TOKEN']

            # code to get TOKEN value from TOKEN.json file
            # TODO: Remove below codes before deploying
            import json
            with open('TOKEN.json', 'r', encoding="UTF-8") as f:
                TOKEN = json.load(f)["TOKEN"]

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