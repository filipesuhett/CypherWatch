import discord
from discord.ext import commands
from loguru import logger
import datetime
from discord import Embed, option
from bot.config import Config

class Discord_Command(commands.Cog):
    def __init__(self, bot):
        """Initializes the Geral_Command class with the bot instance and sets the timezone for Brazil."""
        self.bot = bot
        self.brazil = Config().brazil

    ##############################
    ###### DISCORD COMMANDS ######
    ##############################

    # @commands.slash_command(name="help", description="Show help information", pass_context=True, guild_ids=[Config().guild_id])
    # @checks.is_in_channel(Config)
    # async def help(self, ctx):