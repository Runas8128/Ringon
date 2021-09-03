import discord
from discord.ext import commands

from replit import db

bot = commands.Bot(command_prefix=['!'])

@bot.command(name='강의생성')
async def CreateLecture(ctx, name):
    db['Lecture'][name] = []
    await ctx.send('ok')

@bot.command(name='강의등록')
async def AssignLecture(ctx, name):
    db['Lecture'][name].append(name)
    await ctx.send('ok')

