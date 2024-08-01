from discord import Embed
from discord.ext import commands
from bot.config import Config
import random

class Discord_Command(commands.Cog):
    def __init__(self, bot):
        """Initializes the Discord_Command class with the bot instance and sets the timezone for Brazil."""
        self.bot = bot
        self.brazil = Config().brazil

    ##############################
    ###### DISCORD COMMANDS ######
    ##############################

    @commands.slash_command(name="help", description="Show help information", pass_context=True, guild_ids=[Config().guild_id])
    async def help(self, ctx):
        embed = Embed(title="Help", description="Here are the available commands:", color=0x00ff00)

        # Percorrer todos os comandos registrados no bot
        for cog in self.bot.cogs.values():
            for command in cog.walk_commands():
                embed.add_field(name=f"/{command.name}", value=command.description or "No description", inline=False)
        
        await ctx.respond(embed=embed)
        
    @commands.slash_command(name="info", description="information about stats acronyms", pass_context=True, guild_ids=[Config().guild_id])
    async def info(self, ctx):
        embed = Embed(title="Acronyms", description="Here are the available acronyms:", color=0x00ff00)
        embed.add_field(
            name="KD",
            value="Kill/Death Ratio: The ratio of kills to deaths.",
            inline=False
        )
        embed.add_field(
            name="KDA",
            value="Kill/Death/Assist Ratio: The ratio of kills, deaths, and assists.",
            inline=False
        )
        embed.add_field(
            name="HS%",
            value="Headshot Percentage: The percentage of kills that were headshots.",
            inline=False
        )
        embed.add_field(
            name="ACS",
            value="Average Combat Score: The average score based on performance in combat.",
            inline=False
        )
        embed.add_field(
            name="ADR",
            value="Average Damage per Round: The average damage dealt per round.",
            inline=False
        )
        embed.set_footer(text="Cypher Watch | Data from Valorant API")
        
        await ctx.respond(embed=embed)
        
    @commands.slash_command(name="coinflip", description="Show help information", pass_context=True, guild_ids=[Config().guild_id])
    async def help(self, ctx):
        random_number = random.randint(0, 1)
        
        if random_number == 0:
            await ctx.respond("Heads")
        else:
            await ctx.respond("Tails")
        
