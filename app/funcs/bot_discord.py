import os
import pytz
import json
import discord
from funcs.button_account import Button_account
from bot.config import Config
from funcs.func_aux import find_player_data

async def last_five_matches(ctx, user):
    if len(user.valorant_accounts) == 0:
        await ctx.respond("You need to add at least one Valorant account first!", ephemeral=True)
        return
    elif len(user.valorant_accounts) == 1:
        puuid = user.valorant_accounts[0].puuid
        region = user.valorant_accounts[0].region
        api_key = Config().api_key
        await find_player_data(puuid, region, api_key, ctx)
        return
    else:
        try:
            account_val_name_1 = user.valorant_accounts[0].account_name
            account_val_name_2 = user.valorant_accounts[1].account_name
            view = Button_account() 
            message = await ctx.respond(f"Press the button to select your account. Account 1: {account_val_name_1}, Account 2: {account_val_name_2}", view=view)
            await view.wait()
            if view.value is None:
                await message.edit(content='Timeout. Operation canceled.', view=None)
                return
            elif view.value == 1:
                await message.edit(content='Next step...', view=None)
                puuid = user.valorant_accounts[0].puuid
                region = user.valorant_accounts[0].region
                api_key = Config().api_key
                await find_player_data(puuid, region, api_key, ctx)
                return
            elif view.value == 2:
                await message.edit(content='Next step...', view=None)
                puuid = user.valorant_accounts[1].puuid
                region = user.valorant_accounts[1].region
                api_key = Config().api_key
                await find_player_data(puuid, region, api_key, ctx)
                return              
            else:
                await message.edit(content='Operation canceled.', view=None)
                return

        except Exception as e:
            print(e)