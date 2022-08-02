from typing import Tuple, Dict

import discord
import discord.ui

class EmbedView(discord.ui.View):
    """View object that provides auto traveling for `discord.Embed`.
    TODO: make remover: called when add new embed for same purpose
    """
    def __init__(self, tarInter: discord.Interaction, title: str, description: str, *fields: Tuple[str, str]):
        super().__init__()

        self.baseEmbed = discord.Embed(title=title, description=description, color=0x72e4f3)
        self.fields = fields
        self.count = len(fields)
        self.topIndex = 0
    
    async def update(self, interaction: discord.Interaction):
        embed = self.baseEmbed.copy()
        for i in range(self.topIndex, self.topIndex+10):
            embed.add_field(name=self.fields[i][0], value=self.fields[i][1])
        
        orgMsg = interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(label="⏫", style=discord.ButtonStyle.blurple)
    async def buttonTop(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex = 0
        await self.update(interaction)
    
    @discord.ui.button(label="🔼", style=discord.ButtonStyle.blurple)
    async def buttonUp(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex -= 10
        if self.topIndex < 0: self.topIndex = 0
        await self.update(interaction)
    
    @discord.ui.button(label="🔽", style=discord.ButtonStyle.blurple)
    async def buttonDown(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex += 10
        if self.topIndex > self.count - 10: self.topIndex = self.count - 10
        await self.update(interaction)
    
    @discord.ui.button(label="⏬", style=discord.ButtonStyle.blurple)
    async def buttonBottom(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.topIndex = self.count - 10
        await self.update(interaction)
