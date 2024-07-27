import aiohttp
import pytz
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

async def embed_matches(match_data_list, ctx, one_to_five_matchs):
    if one_to_five_matchs == 1:
        title = "**Resume Last Match**"
    else:
        title = f"**Resume Last {one_to_five_matchs} Matches**"
    embed = discord.Embed(
        title=title,
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
            name=f"**Result:** {match_data['result']} - {match_data['position']}",
            value=(
                f"**🕹️ Info:**\n"
                f"**Map:** {match_data['map_name']}\n"
                f"**Mode:** {match_data['mode']}\n"
                f"**Nickname:** {match_data['nickname']}\n"
                f"**Character:** {match_data['character']}\n\n"
                f"**🎯 Performance:**\n"
                f"**Stats:** {match_data['kills']}/{match_data['deaths']}/{match_data['assists']}\n"
                f"**KD:** {match_data['kd']}\n"
                f"**KDA:** {match_data['kda']}\n"
                f"**HS%:** {match_data['headshot_percentage']}\n"
                f"**ACS:** {match_data['acs']}\n"
                f"**ADR:** {match_data['damage_per_round']}\n\n"
                f"**📈 Rank Change:**\n"
                f"**Tier:** {match_data['tier_patched']}\n"
                f"{rr_points}"
                f"{bar_list}\n\n"
                f"**For more information about acronymos type /info**"
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

async def find_player_data(puuid, region, api_key, ctx, one_to_five_matchs):
    cont = 0
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
        if cont == one_to_five_matchs:
            break
        metadata = match.get("metadata", {})
        map_name = metadata.get("map", "Unknown")
        match_id = metadata.get("matchid", "Unknown")
        mode = metadata.get("mode", "Unknown")
        aux = 0
        count = 0
        
        players = match.get("players", {}).get("all_players", [])

        # Ordenando os jogadores pela pontuação (score) em ordem decrescente
        sorted_players = sorted(players, key=lambda x: x['stats']['score'], reverse=True)

        for player in sorted_players:
            count += 1
            if player.get("puuid") == puuid:
                nickname = f"{player.get('name', 'Unknown')}#{player.get('tag', 'Unknown')}"
                character = player.get("character", "Unknown")
                player_stats = player.get("stats", {})
                kills = player_stats.get("kills", 0)
                assists = player_stats.get("assists", 0)
                deaths = player_stats.get("deaths", 0)
                rounds = metadata.get("rounds_played", 0)
                score = player_stats.get("score", 0)
                headshots = player_stats.get("headshots", 0)
                bodyshots = player_stats.get("bodyshots", 0)
                legshots = player_stats.get("legshots", 0)
                acs = round(score/rounds, 1)
                kd = round(kills/deaths, 2)
                kda = round((kills + assists)/deaths, 2)
                damage_made = player.get("damage_made", 0)
                damage_per_round = round(damage_made/rounds, 1)
                
                # Calculando a soma total de tiros
                total_shots = headshots + bodyshots + legshots

                # Calculando a porcentagem de headshots
                if total_shots > 0:
                    headshot_percentage = (headshots / total_shots) * 100
                    headshot_percentage_rounded = round(headshot_percentage, 0)
                else:
                    headshot_percentage_rounded = 0.00
                
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
                    
                                    
                if count == 1:
                    position = f"{count}st"
                elif count == 2:
                    position = f"{count}nd"
                elif count == 3:
                    position = f"{count}rd"
                else:
                    position = f"{count}th"
                    
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
                    "result": result,
                    "damage_per_round": damage_per_round,
                    "acs": acs,
                    "kd": kd,
                    "kda": kda,
                    "headshot_percentage": headshot_percentage_rounded,
                    "position": position
                    
                }

                match_data_list.append(match_data)
                
                cont += 1

    if match_data_list:
        await embed_matches(match_data_list, ctx, one_to_five_matchs)
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
    cont = 0
    aux = 0
    
    if isinstance(data, dict):
        metadata = data.get("metadata", {})
        map_name = metadata.get("map", "Unknown")
        match_id = metadata.get("matchid", "Unknown")
        mode = metadata.get("mode", "Unknown")
        
        players = data.get("players", {}).get("all_players", [])

        # Ordenando os jogadores pela pontuação (score) em ordem decrescente
        sorted_players = sorted(players, key=lambda x: x['stats']['score'], reverse=True)

        for player in sorted_players:
            cont += 1
            if player.get("puuid") == puuid:
                nickname = f"{player.get('name', 'Unknown')}#{player.get('tag', 'Unknown')}"
                character = player.get("character", "Unknown")
                player_stats = player.get("stats", {})
                kills = player_stats.get("kills", 0)
                assists = player_stats.get("assists", 0)
                deaths = player_stats.get("deaths", 0)
                rounds = metadata.get("rounds_played", 0)
                score = player_stats.get("score", 0)
                headshots = player_stats.get("headshots", 0)
                bodyshots = player_stats.get("bodyshots", 0)
                legshots = player_stats.get("legshots", 0)
                acs = round(score/rounds, 1)
                kd = round(kills/deaths, 2)
                kda = round((kills + assists)/deaths, 2)
                damage_made = player.get("damage_made", 0)
                damage_per_round = round(damage_made/rounds, 1)
                
                # Calculando a soma total de tiros
                total_shots = headshots + bodyshots + legshots

                # Calculando a porcentagem de headshots
                if total_shots > 0:
                    headshot_percentage = (headshots / total_shots) * 100
                    headshot_percentage_rounded = round(headshot_percentage, 0)
                else:
                    headshot_percentage_rounded = 0.00
                
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
                    
                if cont == 1:
                    position = f"{cont}st"
                elif cont == 2:
                    position = f"{cont}nd"
                elif cont == 3:
                    position = f"{cont}rd"
                else:
                    position = f"{cont}th"
                
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
                    "result": result,
                    "damage_per_round": damage_per_round,
                    "acs": acs,
                    "kd": kd,
                    "kda": kda,
                    "headshot_percentage": headshot_percentage_rounded,
                    "position": position
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
        name=f"**Result:** {match_data['result']} - {match_data['position']}",
        value=(
            f"**🕹️ Info:**\n"
            f"**Map:** {match_data['map_name']}\n"
            f"**Mode:** {match_data['mode']}\n"
            f"**Nickname:** {match_data['nickname']}\n"
            f"**Character:** {match_data['character']}\n\n"
            f"**🎯 Performance:**\n"
            f"**Stats:** {match_data['kills']}/{match_data['deaths']}/{match_data['assists']}\n"
            f"**KD:** {match_data['kd']}\n"
            f"**KDA:** {match_data['kda']}\n"
            f"**HS%:** {match_data['headshot_percentage']}\n"
            f"**ACS:** {match_data['acs']}\n"
            f"**ADR:** {match_data['damage_per_round']}\n\n"
            f"**📈 Rank Change:**\n"
            f"**Tier:** {match_data['tier_patched']}\n"
            f"{rr_points}"
            f"{bar_list}\n\n"
            f"**For more information about acronymos type /info**"
        ),
        inline=False
    )
    embed.set_footer(text="Cypher Watch | Data from Valorant API")

    return embed

async def account_data(puuid, region, api_key):
    url = f'https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr-history/{region}/{puuid}'
    params = {'api_key': api_key}
    response_data = {}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    response_data = await response.json()
                else:
                    print(f'Error: {response.status}')
                    response_data = {"data": []}
    except asyncio.TimeoutError:
        print('Request timed out')

    if 'data' not in response_data:
        print("Chave 'data' não encontrada na resposta da API:")
        print(response_data)
        return None

    if len(response_data["data"]) == 0:
        print("Nenhum dado encontrado na resposta da API.")
        progress_bar = create_progress_bar(0, 100)
        
        result = {
            "currenttierpatched": "Unrated",
            "elo": 0,
            "name": response_data["name"],
            "tag": response_data["tag"],
            "total_mmr_change": 0,
            "ranking_in_tier": 0,
            "progress_bar": progress_bar
        }
        return result

# Supondo que 'response_data' já esteja definido anteriormente
    first_response = response_data["data"][0]
    currenttierpatched = first_response["currenttierpatched"]
    elo = int(first_response["elo"])
    name = response_data["name"]
    tag = response_data["tag"]
    ranking_in_tier = first_response["ranking_in_tier"]

    # Define a timezone para GMT-3
    gmt_minus_3 = pytz.timezone('Etc/GMT+3')

    # Ajusta a data atual para GMT-3
    target_date = datetime.now(pytz.utc).astimezone(gmt_minus_3).strftime("%A, %B %d, %Y")
    total_mmr_change = 0

    for match in response_data["data"]:
        # Ajusta a data do match para GMT-3
        match_date_utc = datetime.strptime(match["date"], "%A, %B %d, %Y %I:%M %p")
        match_date_gmt_minus_3 = match_date_utc.replace(tzinfo=pytz.utc).astimezone(gmt_minus_3).strftime("%A, %B %d, %Y")
        
        if match_date_gmt_minus_3 == target_date:
            total_mmr_change += match.get("mmr_change_to_last_game", 0)

    if total_mmr_change > 0:
        total_mmr_change = "+" + str(total_mmr_change)
    else:
        total_mmr_change = str(total_mmr_change)
        
    progress_bar = create_progress_bar(ranking_in_tier, 100)

    result = {
        "currenttierpatched": currenttierpatched,
        "elo": elo,
        "name": name,
        "tag": tag,
        "total_mmr_change": total_mmr_change,
        "ranking_in_tier": ranking_in_tier,
        "progress_bar": progress_bar
    }
    
    return result