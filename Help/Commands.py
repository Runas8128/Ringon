from Common import *

class CogHelp(MyCog, name='도움말'):
    """
    도움말에 관련된 카테고리입니다.
    """
    
    # ----- __init__ -----

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.T = Translator('Help')

        self.AdminOnly = []
        self.OwnerOnly = []

        self.EngCmd = [self.RG_Help_EN]
        self.KorCmd = [self.RG_Help_KR]

    # ----- Command helper -----

    def getAllCommand(self, cog: MyCog, isAdmin: bool, isOwner: bool, lang: Lang):
        command_list: cmdList = [
            command for command in cog.get_commands()
            if (lang == 'KR') == (command in cog.KorCmd)
        ]

        if not isAdmin:
            command_list = [command for command in command_list if command not in cog.AdminOnly]
        if not isOwner:
            command_list = [command for command in command_list if command not in cog.OwnerOnly]
        
        return command_list

    async def HelpBase(self, ctx:commands.Context, lang: Lang):
        embed = discord.Embed(
            title=self.T.translate('Base.Title', lang),
            color=RGColHex
        )
        embed.add_field(
            name=self.T.translate('Base.Basic.Usage', lang),
            value=self.T.translate('Base.Basic.Brief', lang),
            inline=False
        )
        embed.add_field(
            name=self.T.translate('Base.Category.Usage', lang),
            value=self.T.translate('Base.Category.Brief', lang),
            inline=False
        )
        embed.add_field(
            name=self.T.translate('Base.Command.Usage', lang),
            value=self.T.translate('Base.Command.Brief', lang),
            inline=False
        )
        embed.add_field(
            name=self.T.translate('Base.Alias.Usage', lang),
            value=self.T.translate('Base.Alias.Brief', lang),
            inline=False
        )

        await ctx.send(embed=embed)

    async def Help(self, ctx: commands.Context, cmd: str, lang: Lang):
        atr: discord.Member = ctx.author
        isAdmin: bool = atr.guild_permissions.administrator
        isOwner: bool = atr.id == self.bot.owner_id

        if cmd == '':
            embed = discord.Embed(
                title=self.T.translate('Basic.Title', lang),
                description=self.T.translate('Basic.Desc', lang),
                color=RGColHex
            )

            for cogName in self.bot.cogs.keys():
                if cogName in ['매니저', '디버그']:
                    continue

                command_list = self.getAllCommand(self.bot.get_cog(cogName), isAdmin, isOwner, lang)

                if command_list:
                    embed.add_field(
                        name=self.T.translate('Basic.Field', lang).format(cogName),
                        value=' '.join([command.name for command in command_list]),
                        inline=False
                    )

            await ctx.send(embed=embed)
        
        elif cmd in ['별명', 'alias']:
            embed = discord.Embed(
                title=self.T.translate('Alias.Title', lang),
                color=RGColHex
            )

            for cogName in self.bot.cogs.keys():
                if cogName in ['매니저', '디버그']:
                    continue

                command_list = [
                    command for command in self.getAllCommand(self.bot.get_cog(cogName), isAdmin, isOwner, lang)
                    if len(command.aliases) > 0
                ]

                if command_list:
                    embed.add_field(
                        name=self.T.translate('Alias.Field', lang).format(cogName),
                        value='\n'.join([command.name + ' : ' + ', '.join(command.aliases) for command in command_list]),
                        inline=False
                    )

            await ctx.send(embed=embed)

        elif cmd in [c.name for c in self.bot.commands]:
            cmd: commands.Command = self.bot.get_command(cmd)

            if ((not isAdmin) and (cmd in cmd.cog.AdminOnly)) or ((not isOwner) and (cmd in cmd.cog.OwnerOnly)):
                await self.HelpBase(ctx, lang)

            else:
                embed = discord.Embed(
                    title=self.T.translate('Command.Title', lang).format(cmd),
                    description=cmd.brief,
                    color=RGColHex
                )
                embed.add_field(
                    name=self.T.translate('Command.Usage', lang),
                    value=cmd.usage,
                    inline=False
                )
                embed.add_field(
                    name=self.T.translate('Command.Desc', lang),
                    value=cmd.description,
                    inline=False
                )
        
                await ctx.send(embed=embed)
        
        elif cmd in self.bot.cogs.keys() and (cmd not in ['매니저, 디버그'] or atr.id == 449837429885763584):
            cog: commands.Cog = self.bot.get_cog(cmd)
            
            embed = discord.Embed(
                title=self.T.translate('Category.Title', lang).format(cmd),
                description=cog.description,
                color=RGColHex
            )
            for command in self.getAllCommand(cog, isAdmin, isOwner, lang):
                embed.add_field(name='!' + command.name, value=command.brief, inline=False)

            await ctx.send(embed=embed)
        
        else:
            await self.HelpBase(ctx, lang)

    # ----- Commands

    @commands.command(
        name='명령어', aliases=['도움말'],
        brief='도움말을 보여줍니다.',
        description='도움말을 보여줍니다. 명령어 및 카테고리의 간단한 설명은 덤입니다(?)',
        usage='!명령어 (명령어/카테고리 이름 - 생략가능)'
    )
    async def RG_Help_KR(self, ctx: commands.Context, cmd: str=''):
        await self.Help(ctx, cmd, 'KR')
    
    @commands.command(
        name='help',
        brief='show help message',
        description='show help message. you can see some brief for commands or category.',
        usage='!help (command/category name - can be skiped)'
    )
    async def RG_Help_EN(self, ctx: commands.Context, cmd: str=''):
        await self.Help(ctx, cmd, 'EN')
