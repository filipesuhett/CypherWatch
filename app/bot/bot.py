import discord
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self, command_prefix, help_command, intents):
        super().__init__(command_prefix=command_prefix, help_command=help_command, intents=intents)

    async def on_ready(self):
        print(f"{self.user.name} has connected to Discord!")