import discord
from discord.ext import commands
from bot.config import Config
from bot.user import User
from funcs.func_aux import account_check
from funcs.button_account import Button_to_mark

class Users_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.brazil = Config().brazil

    @commands.slash_command(name="add_account", description="Add a Valorant account to your profile", pass_context=True, guild_ids=[Config().guild_id])
    async def add_account(self, ctx, account_name: str):
        await ctx.defer()
        config = Config()
        # Encontra o usuário registrado ou registra um novo
        user = next((u for u in config.users if u.discord_id == ctx.author.id), None)
        
        if user is None:
            user = config.add_user(ctx.author.id)
            if user is None:
                await ctx.respond("There was an error registering the user. Please try again.", ephemeral=True)
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
        
        view = Button_to_mark() 
        message = await ctx.respond(f"Do you want to be tagged when we notify you of a new match on this account?", view=view)
        await view.wait()
        if view.value is None:
            await message.edit(content='Timeout. Operation canceled.', view=None)
            return
        elif view.value == 1:
            await message.edit(view=None)
            tag_me = True
        elif view.value == 2:
            await message.edit(view=None)
            tag_me = False      
        else:
            await message.edit(content='Operation canceled.', view=None)
            return
        
        aux = user.add_account(account_name, tag_me)
        # Adiciona a conta Valorant
        if aux:
            config.save_users()  # Salva as mudanças no arquivo JSON
            await message.edit(content=f"Account '{account_name}' added successfully!", view=None)
        else:
            await message.edit(content=f"Account '{account_name}' is already added.", view=None)
            
            
    @commands.slash_command(name="remove_account", description="Remove a Valorant account from your profile", pass_context=True, guild_ids=[Config().guild_id])
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
