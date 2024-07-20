import discord
from discord.ext import commands
from discord.ui import Button, View

class Button_account(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Account 1', style=discord.ButtonStyle.blurple)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = 1
        self.stop()

    @discord.ui.button(label='Account 2', style=discord.ButtonStyle.blurple)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = 2
        self.stop()