from .Helper import *

class OpenCog(MyCog, name='오픈'):
    """
    이번 오픈에 대한 정보를 가져옵니다.
    """
    
    @commands.command(
        name="찾기", aliases=['검색', 'find'],
        brief='오픈 정보에서 플레이어를 검색합니다.',
        description='오픈 정보에서 플레이어를 검색합니다.',
        usage='!찾기/!find (이름)'
    )
    async def find(self, ctx: commands.Context, *name: str):
        name = ' '.join(name)
        
        if name in table['A'].players:
            cls1, cls2 = table['A'].players[name]
            
            embed = discord.Embed(title=name + "님의 덱입니다", description=name + "님은 A조입니다.")
            embed.add_field(name=cls1[0], value=cls1[1])
            embed.add_field(name=cls2[0], value=cls2[1])
            await ctx.send(embed=embed)
        elif name in table['B'].players:
            cls1, cls2 = table['B'].players[name]
            
            embed = discord.Embed(title=name + "님의 덱입니다", description=name + "님은 B조입니다.")
            embed.add_field(name=cls1[0], value=cls1[1])
            embed.add_field(name=cls2[0], value=cls2[1])
            await ctx.send(embed=embed)
        else:
            await ctx.send("닉네임을 찾지 못했습니다")
    
    @commands.command(
        name="참가자", aliases=['플레이어', 'player', 'players'],
        brief='A/B조의 참가자를 모두 보여줍니다.',
        description='A/B조의 참가자를 모두 보여줍니다.',
        usage='!참가자/!player A/B'
    )
    async def player(self, ctx: commands.Context, AB: str = ""):
        AB = AB.upper()[0]
        if AB == 'A':
            players = list(table['A'].players.keys())
            embed = discord.Embed(title="A조 참가자")
            for i in range(0, len(players), 10):
                embed.add_field(name=f'{i+1}~{min(i+10, len(players))}', value=', '.join(players[i:i+10]), inline=False)
            await ctx.send(embed=embed)
        elif AB == 'B':
            players = list(table['B'].players.keys())
            embed = discord.Embed(title="A조 참가자")
            for i in range(0, len(players), 10):
                embed.add_field(name=f'{i+1}~{min(i+10, len(players))}', value=', '.join(players[i:i+10]), inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("A조와 B조 중에 골라주세요! 첫 글자만 인식됩니다.")
