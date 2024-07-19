# commands/match.py
import discord
from discord.ext import commands
from bot.config import Config
from bot.user import User

class Match_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.brazil = Config().brazil

    @commands.slash_command(name="get_last_five_matches", description="Get the last five matches", pass_context=True, guild_ids=[Config().guild_id])
    async def register(self, ctx):
        await ctx.defer()
        config = Config()
        if any(user.discord_id == ctx.author.id for user in config.users):
            user = next((u for u in config.users if u.discord_id == ctx.author.id), None)
            if user is not None:
                await last_five_matches(ctx, user)
            else:
                await ctx.respond("You need to register first!", ephemeral=True)
        else:
            await ctx.respond("You need to register first!", ephemeral=True)
