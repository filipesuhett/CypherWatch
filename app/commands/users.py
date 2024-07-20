# commands/users.py
import discord
from discord.ext import commands
from bot.config import Config
from bot.user import User
from funcs.func_aux import account_check

class Users_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.brazil = Config().brazil

    @commands.slash_command(name="register", description="Register a new user", pass_context=True, guild_ids=[Config().guild_id])
    async def register(self, ctx):
        await ctx.defer()
        config = Config()
        if any(user.discord_id == ctx.author.id for user in config.users):
            await ctx.respond("You are already registered!", ephemeral=True)
            return
        user = ctx.author
        User(user.id)
        await ctx.respond(f"User {user.name} registered successfully!", ephemeral=True)

    @commands.slash_command(name="add_account", description="Add a Valorant account to your profile", pass_context=True, guild_ids=[Config().guild_id])
    async def add_account(self, ctx, account_name: str):
        await ctx.defer()
        config = Config()
        user = next((u for u in config.users if u.discord_id == ctx.author.id), None)
        
        if user is None:
            await ctx.respond("You need to register first!", ephemeral=True)
            return
        
        if len(user.valorant_accounts) == 2:
            await ctx.respond(f"Max 2 accounts", ephemeral=True)
            return
        
        if "#" not in account_name:
            await ctx.respond(f"Account '{account_name}' is not valid.", ephemeral=True)
            return
        
        if await account_check(account_name) == False:
            await ctx.respond(f"Account '{account_name}' is not valid.", ephemeral=True)
            return
        
        aux = user.add_account(account_name)
        # Adiciona a conta Valorant
        if aux == True:
            config.save_users()  # Salva as mudanças no arquivo JSON
            await ctx.respond(f"Account '{account_name}' added successfully!", ephemeral=True)
        else:
            await ctx.respond(f"Account '{account_name}' is already added.", ephemeral=True)
            
    @commands.slash_command(name="remove_account", description="Get user data", pass_context=True, guild_ids=[Config().guild_id])
    async def remove_account(self, ctx, account_name: str):
        await ctx.defer()
        config = Config()
        # Encontra o usuário registrado
        user = next((u for u in config.users if u.discord_id == ctx.author.id), None)
        
        if user is None:
            await ctx.respond("You need to register first!", ephemeral=True)
            return
        
        # Remove a conta Valorant
        if user.remove_account(account_name):
            config.save_users()  # Salva as mudanças no arquivo JSON
            await ctx.respond(f"Account '{account_name}' removed successfully!", ephemeral=True)
        else:
            await ctx.respond(f"Account '{account_name}' is not added.", ephemeral=True)