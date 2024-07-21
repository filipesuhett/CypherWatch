import aiohttp
import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime, timedelta, timezone

def create_progress_bar(value, max_value, length=10):
    progress = int((value / max_value) * length)
    bar = '█' * progress + '░' * (length - progress)
    return bar


async def account_check(account_name):
    nickname, tag = account_name.split('#')
    url = f'https://api.henrikdev.xyz/valorant/v1/account/{nickname}/{tag}'
    params = {'api_key': 'HDEV-7ec2639e-80ba-4ed5-b1f5-efc19d248be6'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return True
                else:
                    print(f'Error fetching account data: {response.status}')
    except asyncio.TimeoutError:
        print('Request timed out')
    return False

async def get_mmr_by_match_id(match_id, puuid, region, api_key):
    url = f"https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr-history/{region}/{puuid}"
    params = {'api_key': api_key}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    for record in data["data"]:
                        if record["match_id"] == match_id:
                            return record
                else:
                    print(f'Error fetching MMR data: {response.status}')
    except asyncio.TimeoutError:
        print('Request timed out')
    return None

async def embed_matches(match_data_list, ctx):
    embed = discord.Embed(
        title="**Resume Last 5 Matches**",
        color=0x1abc9c
    )

    for i, match_data in enumerate(match_data_list):
        if i > 0:
            embed.add_field(name="\u200b", value="---", inline=False)
        # Supondo que `ranking_in_tier` vá de 0 a 100
        ranking_in_tier = match_data['ranking_in_tier']
        progress_bar = create_progress_bar(ranking_in_tier, 100)
        mmr_change_aux = match_data['mmr_change']
        if "+" in mmr_change_aux:
            mmr_change_aux = mmr_change_aux.replace("+", "")
        else:
            mmr_change_aux = mmr_change_aux.replace("-", "")
        mmr_change_aux = int(mmr_change_aux)
        
        if mmr_change_aux > ranking_in_tier and "+" in match_data['mmr_change']:
            rr_points = f"**Rank Points Change:** RANK UP CONGRATULATIONS\n"
            bar_list = f"**Ranking in Tier:** {progress_bar} {ranking_in_tier}/100 - RANK UP"
        elif (- mmr_change_aux) + ranking_in_tier == 100:
            rr_points = f"**Rank Points Change:** RANK DOWN ITS SAD\n"
            bar_list = f"**Ranking in Tier:** {progress_bar} {ranking_in_tier}/100 - RANK DOWN ITS SAD"
        else:
            rr_points = f"**Rank Points Change:** {match_data['mmr_change']}\n"
            bar_list = f"**Ranking in Tier:** {progress_bar} {ranking_in_tier}/100"
        
        
        embed.add_field(
            name=f"**Result:** {match_data['result']}",
            value=(
                f"**🕹️ Info:**\n"
                f"**Map:** {match_data['map_name']}\n"
                f"**Mode:** {match_data['mode']}\n"
                f"**Nickname:** {match_data['nickname']}\n"
                f"**Character:** {match_data['character']}\n\n"
                f"**🎯 Performance:**\n"
                f"**KDA:** {match_data['kills']}/{match_data['deaths']}/{match_data['assists']}\n\n"
                f"**📈 Rank Change:**\n"
                f"**Tier:** {match_data['tier_patched']}\n"
                f"{rr_points}"
                f"{bar_list}"
            ),
            inline=False
        )


    embed.set_footer(text="Cypher Watch | Data from Valorant API")

    if isinstance(ctx, commands.Context):
        await ctx.send(embed=embed)
    elif isinstance(ctx, discord.Interaction):
        await ctx.response.send_message(embed=embed)
    elif isinstance(ctx, discord.commands.context.ApplicationContext):
        await ctx.respond(embed=embed)
    else:
        print("ctx is not a valid commands.Context, discord.Interaction, or ApplicationContext object")

async def find_player_data(puuid, region, api_key, ctx):
    url = f'https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/{region}/{puuid}'
    params = {'api_key': api_key}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    response_data = await response.json()
                else:
                    print(f'Error fetching player data: {response.status}')
                    return
    except asyncio.TimeoutError:
        print('Request timed out')
        return
    
    match_data_list = []

    for match in response_data.get("data", []):
        metadata = match.get("metadata", {})
        map_name = metadata.get("map", "Unknown")
        match_id = metadata.get("matchid", "Unknown")
        mode = metadata.get("mode", "Unknown")
        aux = 0

        for player in match.get("players", {}).get("all_players", []):
            if player.get("puuid") == puuid:
                nickname = f"{player.get('name', 'Unknown')}#{player.get('tag', 'Unknown')}"
                character = player.get("character", "Unknown")
                player_stats = player.get("stats", {})
                kills = player_stats.get("kills", 0)
                assists = player_stats.get("assists", 0)
                deaths = player_stats.get("deaths", 0)
                
                mmr_data = await get_mmr_by_match_id(match_id, puuid, region, api_key)
                
                if mmr_data:
                    mmr_change = mmr_data.get("mmr_change_to_last_game", "N/A")
                    tier_patched = mmr_data.get("currenttierpatched", "N/A")
                    ranking_in_tier = mmr_data.get("ranking_in_tier", "N/A")
                    
                    if isinstance(mmr_change, (int, float)):
                        mmr_change = f"+{mmr_change}" if mmr_change > 0 else str(mmr_change)
                else:
                    mmr_change = "N/A"
                    tier_patched = "N/A"
                    ranking_in_tier = "N/A"
                    
                for player in match.get("players", {}).get("red", []):
                    if player.get("puuid") == puuid:
                        aux = 1
                        
                if aux == 1:
                    team = "red"
                else:
                    team = "blue"
                    
                has_won = match.get("teams", {}).get(team, {}).get("has_won", False)
                
                if has_won == True:
                    result = "Vitory"
                else:
                    result = "Defeat"
                    
                match_data = {
                    "map_name": map_name,
                    "match_id": match_id,
                    "mode": mode,
                    "kills": kills,
                    "assists": assists,
                    "deaths": deaths,
                    "tier_patched": tier_patched,
                    "ranking_in_tier": ranking_in_tier,
                    "mmr_change": mmr_change,
                    "character": character,
                    "nickname": nickname,
                    "result": result
                }

                match_data_list.append(match_data)

    if match_data_list:
        await embed_matches(match_data_list, ctx)
    else:
        await ctx.send("No match data found.")

async def find_player_match_data(match_id, puuid, region, api_key):
    url = f"https://api.henrikdev.xyz/valorant/v2/match/{match_id}"
    params = {'api_key': api_key}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    response_data = await response.json()
                else:
                    print(f'Error fetching match data: {response.status}')
                    return None
    except asyncio.TimeoutError:
        print('Request timed out')
        return None

    match_data = None
    data = response_data.get("data", {})
    aux = 0
    
    if isinstance(data, dict):
        metadata = data.get("metadata", {})
        map_name = metadata.get("map", "Unknown")
        match_id = metadata.get("matchid", "Unknown")
        mode = metadata.get("mode", "Unknown")

        for player in data.get("players", {}).get("all_players", []):
            if player.get("puuid") == puuid:
                nickname = f"{player.get('name', 'Unknown')}#{player.get('tag', 'Unknown')}"
                character = player.get("character", "Unknown")
                player_stats = player.get("stats", {})
                kills = player_stats.get("kills", 0)
                assists = player_stats.get("assists", 0)
                deaths = player_stats.get("deaths", 0)
                
                mmr_data = await get_mmr_by_match_id(match_id, puuid, region, api_key)
                
                if mmr_data:
                    mmr_change = mmr_data.get("mmr_change_to_last_game", "N/A")
                    tier_patched = mmr_data.get("currenttierpatched", "N/A")
                    ranking_in_tier = mmr_data.get("ranking_in_tier", "N/A")
                    
                    if isinstance(mmr_change, (int, float)):
                        mmr_change = f"+{mmr_change}" if mmr_change > 0 else str(mmr_change)
                else:
                    mmr_change = "N/A"
                    tier_patched = "N/A"
                    ranking_in_tier = "N/A"
                    
                for player in data.get("players", {}).get("red", []):
                    if player.get("puuid") == puuid:
                        aux = 1
                        
                if aux == 1:
                    team = "red"
                else:
                    team = "blue"
                    
                has_won = data.get("teams", {}).get(team, {}).get("has_won", False)
                
                if has_won == True:
                    result = "Vitory"
                else:
                    result = "Defeat"
                
                match_data = {
                    "map_name": map_name,
                    "match_id": match_id,
                    "mode": mode,
                    "kills": kills,
                    "assists": assists,
                    "deaths": deaths,
                    "tier_patched": tier_patched,
                    "ranking_in_tier": ranking_in_tier,
                    "mmr_change": mmr_change,
                    "character": character,
                    "nickname": nickname,
                    "result": result
                }
                break
        if match_data:
            return match_data
    
    return None

async def verify_match(puuid, region, api_key):
    url = f'https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr-history/{region}/{puuid}'
    params = {'api_key': api_key}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    print(f'Error: {response.status}')
                    data = {"data": []}
    except asyncio.TimeoutError:
        print('Request timed out')
        data = {"data": []}

    current_time = datetime.now(timezone.utc)
    five_minutes_ago = current_time - timedelta(minutes=18)

    for match in data.get('data', []):
        if isinstance(match, dict):
            match_time = match.get("date_raw", 0)
            match_id = match.get("match_id", '')
            url_match = f"https://api.henrikdev.xyz/valorant/v2/match/{match_id}"
            params = {'api_key': api_key}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url_match, params=params, timeout=10) as response:
                        if response.status == 200:
                            response_data = await response.json()
                        else:
                            print(f'Error: {response.status}')
                            response_data = {"data": []}
            except asyncio.TimeoutError:
                print('Request timed out')
            data = response_data.get("data", {})
            
            if isinstance(data, dict):
                metadata = data.get("metadata", {})
                game_length = metadata.get("game_length", 0)
                match_time += game_length
                match_time = datetime.fromtimestamp(match_time, timezone.utc)
                print(f"Match played at {match_time}. vs {five_minutes_ago} - {five_minutes_ago - match_time}")
            if match_time > five_minutes_ago:
                match_data = await find_player_match_data(match.get("match_id", ''), puuid, region, api_key)
                if match_data:
                    embed = await embed_match_history(match_data)
                    return embed
        break
    else:
        print("No match played in the last 30 minutes.")
        return False

async def embed_match_history(match_data):
    if match_data["result"] == "Vitory":
        color = 0x00FF00
    else:
        color = 0xe74c3c
    embed = discord.Embed(
        title="**New Match History**",
        color=color
    )
    # Supondo que `ranking_in_tier` vá de 0 a 100
    ranking_in_tier = match_data['ranking_in_tier']
    progress_bar = create_progress_bar(ranking_in_tier, 100)
    mmr_change_aux = match_data['mmr_change']
    if "+" in mmr_change_aux:
        mmr_change_aux = mmr_change_aux.replace("+", "")
    else:
        mmr_change_aux = mmr_change_aux.replace("-", "")
    mmr_change_aux = int(mmr_change_aux)
    
    if mmr_change_aux > ranking_in_tier and "+" in match_data['mmr_change']:
        rr_points = f"**Rank Points Change:** RANK UP CONGRATULATIONS\n"
        bar_list = f"**Ranking in Tier:** {progress_bar} {ranking_in_tier}/100 - RANK UP"
    elif mmr_change_aux + ranking_in_tier == 100:
        rr_points = f"**Rank Points Change:** RANK DOWN ITS SAD\n"
        bar_list = f"**Ranking in Tier:** {progress_bar} {ranking_in_tier}/100 - RANK DOWN"
    else:
        rr_points = f"**Rank Points Change:** {match_data['mmr_change']}\n"
        bar_list = f"**Ranking in Tier:** {progress_bar} {ranking_in_tier}/100"
    
    
    embed.add_field(
        name=f"**Result:** {match_data['result']}",
        value=(
            f"**🕹️ Info:**\n"
            f"**Map:** {match_data['map_name']}\n"
            f"**Mode:** {match_data['mode']}\n"
            f"**Nickname:** {match_data['nickname']}\n"
            f"**Character:** {match_data['character']}\n\n"
            f"**🎯 Performance:**\n"
            f"**KDA:** {match_data['kills']}/{match_data['deaths']}/{match_data['assists']}\n\n"
            f"**📈 Rank Change:**\n"
            f"**Tier:** {match_data['tier_patched']}\n"
            f"{rr_points}"
            f"{bar_list}"
        ),
        inline=False
    )
    embed.set_footer(text="Cypher Watch | Data from Valorant API")

    return embed