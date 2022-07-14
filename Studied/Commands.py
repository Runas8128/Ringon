from .Helper import *

class CogStudied(commands.Cog, name='전체감지'):
    """
    메시지의 전체를 감지하게 하는 명령어 카테고리입니다.
    """
    
    # ----- __init__ -----
    
    def __init__(self, bot):
        self.bot = bot
        
    # ----- Events -----
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        msg = message.content
        
        if msg in studied.taughts:
            await message.channel.trigger_typing()
            await message.channel.send(studied.get(msg))
            return
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return
        
        _id = reaction.message.id
        
        if studied.StudiedEmbedMsg and _id == studied.StudiedEmbedMsg.id:
            if reaction.emoji == '⏫':
                await studied.StudiedEmbedMsg.edit(embed=studied.Top())
            elif reaction.emoji == '🔼':
                await studied.StudiedEmbedMsg.edit(embed=studied.Up())
            elif reaction.emoji == '🔽':
                await studied.StudiedEmbedMsg.edit(embed=studied.Down())
            elif reaction.emoji == '⏬':
                await studied.StudiedEmbedMsg.edit(embed=studied.Bottom())
    
    # ----- Commands -----
    
    @commands.command(
        name='잊어',
        brief='링곤이가 배운 특정 문장을 잊게 합니다.',
        description='링곤이가 배운 특정 문장을 잊게 합니다. 이후에 해당 문장에 반응하지 않습니다.',
        usage='!잊어 (배운 문장)'
    )
    async def RG_Forget(self, ctx: commands.Context, *src: str):
        s: str = ' '.join(src).strip()
        
        if s in studied.taughts:
            studied.rem(s)
            await ctx.send(f'{s}가 기억이 안날지도..?')
        else:
            await ctx.send('그래서 그게 뭐였죠..?')
    
    @commands.command(
        name='능지',
        brief='링곤이가 배운 총 문장의 개수를 보여줍니다.',
        description='링곤이가 배운 총 문장의 개수를 보여줍니다.',
        usage='!능지'
    )
    async def RG_Neungji(self, ctx: commands.Context):
        await ctx.send(f"링곤사전을 보니, 저의 아이큐는 {len(studied.taughts.keys())}이라고 하네요!")
    
    @commands.command(
        name='배운거',
        brief='링곤이가 배운 문장을 모두 알려줍니다.',
        description='링곤이가 배운 문장을 모두 알려줍니다. 10개씩 끊어서 보여주며, 이모지를 눌러서 페이지별로 이동이 가능합니다.',
        usage='!배운거'
    )
    async def RG_Studied(self, ctx: commands.Context):
        iq = len(studied.taughts)
        
        if iq == 0:
            studied.StudiedEmbedMsg = None
            await ctx.send('링곤이 멍청하당.. 헣허')
        
        else:
            studied.StudiedEmbedMsg = await ctx.send(embed=studied.Top())
            
            if iq > 10:
                await studied.StudiedEmbedMsg.add_reaction('🔼')
                await studied.StudiedEmbedMsg.add_reaction('🔽')
            
            if iq > 20:
                await studied.StudiedEmbedMsg.add_reaction('⏫')
                await studied.StudiedEmbedMsg.add_reaction('⏬')
