import discord
import asyncio
from discord.ext import commands
from bot.config import Config
from bot.user import User
from funcs.bot_discord import last_five_matches
from funcs.func_aux import account_data
from discord import Embed, option

class Match_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.brazil = Config().brazil

    @commands.slash_command(name="get_last_matches", description="Get the last five matches", pass_context=True, guild_ids=[Config().guild_id])
    @option("one-to-five-matchs", int, description="Choose a number between 1 and 5", min_value=1, max_value=5)
    async def get_last_five_matches(self, ctx, one_to_five_matchs: int):
        await ctx.defer()
        try:
            config = Config()
            user = next((u for u in config.users if u.discord_id == ctx.author.id), None)
            if user is not None:
                await last_five_matches(ctx, user, one_to_five_matchs)
            else:
                await ctx.respond("You need to register first!", ephemeral=True)
        except Exception as e:
            print(f"Error in get_last_five_matches: {e}")
            await ctx.respond("An error occurred while processing your request.", ephemeral=True)
            
    @commands.slash_command(name='leaderboard', description='Get the leaderboard', pass_context=True, guild_ids=[Config().guild_id])
    async def leaderboard(self, ctx):
        await ctx.defer()
        leaderboard = []
        config = Config()

        count = 0  # Contador para rastrear o número de contas processadas

        for user in config.users:
            for account in user.valorant_accounts:
                account_data_result = await account_data(account.puuid, account.region, Config().api_key)
                if account_data_result:  # Verifique se a resposta não é None
                    leaderboard.append(account_data_result)

                count += 1  # Incrementa o contador

                # Verifica se já processou 5 contas e, se sim, faz uma pausa de 1 minuto
                if count % 11 == 0:
                    print("Pausando por 1 minuto...")
                    await asyncio.sleep(60)  # Delay de 1 minuto

        sorted_leaderboard = sorted(leaderboard, key=lambda x: x["elo"], reverse=True)

        embed = discord.Embed(
            title="Valorant Leaderboard",
            description="Here are the top players for today:",
            color=discord.Color.blue()
        )

        for i, account in enumerate(sorted_leaderboard, start=1):
            player_info = (
                f"**Rank:** {account['currenttierpatched']}\n"
                f"**Ranking in Tier:** {account['progress_bar']} {account['ranking_in_tier']}/100\n"
                f"**RR Change:** {account['total_mmr_change']}\n"
            )
            embed.add_field(
                name=f"{i}. {account['name']}#{account['tag']}",
                value=player_info,
                inline=False
            )

        await ctx.respond(embed=embed)
