#-*- coding: utf-8 -*-

from .Helper import *

class CogProfile(MyCog, name='프로필'):
    """
    프로필을 설정하거나, 보여주는 카테고리입니다.
    Command category for set/show user's profiles
    """

    # ----- __init__ -----

    def __init__(self, bot):
        global profiles
        profiles = Profiles()
        
        self.bot = bot
        self.T = Translator('Profile')

        self.AdminOnly = []
        self.OwnerOnly = []

        self.EngCmd = [self.RG_Profile_EN]
        self.KorCmd = [self.RG_Profile_KR]

    # ----- Command Helper -----

    async def Add(self, ctx: commands.Context, mention: discord.User, cls1: str, cls2: str, lang: Lang):
        if mention and cls1:
            if profiles.isin(mention):
                await ctx.send(self.T.translate('Add.InList', lang))
            elif mention.bot:
                await ctx.send(self.T.translate('Add.Bot', lang))
            else:
                profiles.append(mention.id, cls1, cls2)
                await ctx.send(self.T.translate('Add.Success', lang).format(mention.name))
        else:
            await ctx.send(self.T.translate('Add.Usage', lang))
    
    async def Modify(self, ctx: commands.Context, field: str, newValue: str, lang: Lang):
        fc = field[-1]
        if field not in ['클래스1', '클래스2', 'class1', 'class2']:
            await ctx.send(self.T.translate('Modify.Usage', lang))

        atr: discord.User = ctx.author
        
        profile = profiles.find(atr)
        if not profile:
            await ctx.send(self.T.translate('Modify.NotFoundProf', lang).format(atr.mention))
            return

        if newValue in OrgCls:
            profiles.find(atr)['class1' if fc == '1' else 'class2'] = newValue
            await ctx.send(self.T.translate('Modify.Success', lang).format(atr.mention, fc, newValue))
        elif fc == '2' and newValue in ["삭제", "delete"]:
            profiles.find(atr)['class2'] = None
            await ctx.send(self.T.translate('Modify.Delete', lang).format(atr.mention))
        else:
            await ctx.send(self.T.translate('Modify.InvalidClass', lang))
    
    async def View(self, ctx: commands.Context, tar: discord.User, lang: Lang):
        await ctx.send(embed=profiles.get(tar, lang))

    # ----- Command -----

    @commands.command(
        name='프로필',
        brief='프로필을 설정하거나, 보여줍니다.',
        description='프로필을 설정하거나, 보여줍니다. 자세한 내용은 사용법을 참고해주세요',
        usage='''`!프로필 [멘션 - 기본값: 본인]` -> 프로필 보기
        `!프로필 생성/추가 (멘션) (주력 클래스, 최대 2개)`
        `!프로필 수정 [클래스1/클래스2] (수정할 클래스)` or `!프로필 수정 클래스2 삭제`
        예시: !프로필 수정 클래스1 드래곤'''
    )
    async def RG_Profile_KR(self, ctx: commands.Context, arg1: str = '', arg2: str = '', arg3: str = '', arg4: str = ''):
        tar: discord.Member
        
        if arg2.startswith('<@'):
            tarID = arg2[2:-1].replace('!', '')
            if tarID.isdigit():
                message: discord.Message = ctx.message
                tar = message.guild.get_member(int(tarID))
        elif arg2.isdigit():
            message: discord.Message = ctx.message
            tar = message.guild.get_member(int(arg2))
        else:
            tar = None

        if arg1 in ['생성', '추가']:
            await self.Add(ctx, tar, strToClass(arg3), strToClass(arg4), 'KR')
        elif arg1 == '수정':
            await self.Modify(ctx, arg2.lower(), strToClass(arg3), 'KR')
        else:
            await self.View(ctx, tar, 'KR')

    @commands.command(
        name='profile', aliases=['prof'],
        brief='show/set profile',
        description='show/set profile. See usage to detail',
        usage='''`!profile [mention - default: author]` -> show profile
        `!profile create/make/add [mention] (Main class, up to 2)`
        `!profile modify [class1/class2] (Class Name) or `!profile modify class2 delete``
        e.g. !profile modify class1 dragon'''
    )
    async def RG_Profile_EN(self, ctx: commands.Context, arg1: str = '', arg2: str = '', arg3: str = '', arg4: str = ''):
        tar: discord.Member
        
        if arg2.startswith('<@'):
            tarID = arg2[2:-1].replace('!', '')
            if tarID.isdigit():
                message: discord.Message = ctx.message
                tar = message.guild.get_member(int(tarID))
        elif arg2.isdigit():
            message: discord.Message = ctx.message
            tar = message.guild.get_member(int(arg2))
        else:
            tar = None

        if arg1.lower() in ['create', 'make', 'add']:
            await self.Add(ctx, tar, strToClass(arg3), strToClass(arg4), 'KR')
        elif arg1.lower() == 'modify':
            await self.Modify(ctx, arg2.lower(), strToClass(arg3), 'KR')
        else:
            await self.View(ctx, tar, 'KR')
