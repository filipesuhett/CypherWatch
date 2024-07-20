import discord
from discord.ext import commands
from bot.config import Config
from funcs.bot_discord import last_five_matches

class Match_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.brazil = Config().brazil

    @commands.slash_command(name="get_last_five_matches", description="Get the last five matches", pass_context=True, guild_ids=[Config().guild_id])
    async def get_last_five_matches(self, ctx):
        await ctx.defer()
        try:
            config = Config()
            user = next((u for u in config.users if u.discord_id == ctx.author.id), None)
            if user is not None:
                await last_five_matches(ctx, user)
            else:
                await ctx.respond("You need to register first!", ephemeral=True)
        except Exception as e:
            print(f"Error in get_last_five_matches: {e}")
            await ctx.respond("An error occurred while processing your request.", ephemeral=True)
